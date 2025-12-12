import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely import points as spoints
from ._filter_area import FilterArea
import xarray as xr

def _get_fft_mask(x: np.ndarray, y: np.ndarray, area: Polygon | MultiPolygon):
    """获取FFT频谱的掩码矩阵"""

    # 获取频率点，在此反转时间轴
    X, Y = np.meshgrid(x, -y)
    points = spoints(X.flatten(), Y.flatten())

    mask = np.zeros_like(X, dtype=bool)

    def polygon_mask(area: Polygon):
        """获取单个多边形的掩码"""
        return area.contains(points).reshape(X.shape)

    def flip_polygon(area: Polygon) -> Polygon:
        """以原点为中心翻转多边形"""
        x = np.array(area.exterior.xy[0])
        y = np.array(area.exterior.xy[1])
        return Polygon(np.array([-x, -y]).T)

    # 合并多个多边形的掩码
    if isinstance(area, MultiPolygon):
        for poly in area.geoms:
            mask |= polygon_mask(poly)
            mask |= polygon_mask(flip_polygon(poly))
    else:
        mask |= polygon_mask(area)
        mask |= polygon_mask(flip_polygon(area))

    # 变为 false=0, true=1 的mask
    mask = mask.astype(np.float32)
    return mask


def _fft2_area_filter(data: np.ndarray,
                      filter_area: FilterArea | Polygon | MultiPolygon,
                      x_axes_index: int = -1, y_axes_index: int = -2,
                    x_shift_freq: np.ndarray = None,
                    y_shift_freq: np.ndarray = None,) -> np.ndarray:
    """FFT二维区域滤波，输入的数据可以是n维，保留滤波区域的信号。

    Parameters
    ----------
    data : np.ndarray
        待滤波的数据数组。
    filter_area : FilterArea | Polygon | MultiPolygon
        滤波区域
    x_axes_index : int, optional
        滤波的x维度，应对应经度, by default -1
    y_axes_index : int, optional
        滤波的y维度，应对应时间, by default -2
    x_shift_freq : np.ndarray, optional
        经过 fft_shift 的x频率坐标（零在中心），此坐标为滤波区域的x坐标，
        如未指定则默认使用 np.fft.fftfreq()
    y_shift_freq : np.ndarray, optional
        经过 fft_shift 的y频率坐标（零在中心），此坐标为滤波区域的y坐标，
        如未指定则默认使用 np.fft.fftfreq()

    Returns
    -------
    np.ndarray
        返回滤波后的数据数组
    """

    if isinstance(filter_area, FilterArea):
        area = filter_area.shape
    elif isinstance(filter_area, (Polygon, MultiPolygon)):
        area = filter_area
    else:
        raise TypeError("filter_area must be a Polygon, MultiPolygon or FilterArea")

    if x_shift_freq is None:
        x_shift_freq = np.fft.fftfreq(data.shape[x_axes_index])
        x_shift_freq = np.fft.fftshift(x_shift_freq)
    if y_shift_freq is None:
        y_shift_freq = np.fft.fftfreq(data.shape[y_axes_index])
        y_shift_freq = np.fft.fftshift(y_shift_freq)

    axes = (y_axes_index, x_axes_index)
    data_fft = np.fft.fft2(data, axes=axes)
    data_fft = np.fft.fftshift(data_fft, axes=axes)

    # 获取掩码
    mask = _get_fft_mask(x_shift_freq, y_shift_freq, area)

    # 在axes的维度上乘上mask，拓展 mask 的维度以匹配 data_fft
    mask_shape = [1] * len(data.shape)
    for i, axis in enumerate(axes):
        mask_shape[axis] = data.shape[axis]
    mask = mask.reshape(mask_shape)
    data_fft = data_fft * mask

    # 还原数据
    data_fft = np.fft.ifftshift(data_fft, axes=axes)
    data_fft = np.fft.ifft2(data_fft, axes=axes)

    return np.real(data_fft)


def fft_time_lon_area_filter(data: xr.DataArray,
                filter_area: FilterArea | Polygon | MultiPolygon,
                lon_name: str | int = "longitude", time_name: str | int = "time",
                time_window: bool = True, time_window_alpha: float = 0.1,
                lon_window: bool = False, lon_window_alpha: float = 0.1,
                ) -> xr.DataArray:
    """对 xarray.DataArray 数据进行时间-经度二维FFT区域滤波，保留滤波区域的信号。
    配合 FilterArea 使用，例如提取 Kelvin 波的信号：

    Example
    -------

        >>> uwnd = xr.open_dataarray("uwnd.nc") # (time, lat, lon)
        >>>
        >>> # 提取 Kelvin 波信号
        >>> kelvin_area = mew.KelvinFilterArea()
        >>> kelvin_uwnd = mew.fft_time_lon_area_filter(
        ...     uwnd, kelvin_area,
        ...     lon_name="lon", time_name="time"
        ... )
        >>>
        >>> # 提取符合波数 3~10 zonal_wavenumber，频率 0.2~0.8 cpd 的信号
        >>> rect_area = mew.RectangleFilterArea(
        ...     min_wavenumber=3, max_wavenumber=10,
        ...     min_freq=0.2, max_freq=0.8
        ... )
        >>> rect_uwnd = mew.fft_time_lon_area_filter(
        ...     uwnd, rect_area,
        ...     lon_name="lon", time_name="time"
        ... )


    Parameters
    ----------
    data : xr.DataArray
        需要滤波的数据，必须包含经度与时间维度。
    filter_area : FilterArea | Polygon | MultiPolygon
        滤波区域，将保留区域内的信号，可以是 FilterArea 实例，
        或 shapely 的 Polygon / MultiPolygon 多边形实例，
        多边形的平面坐标需要使用以下单位：

         - x 轴：纬向波数，单位为 'zonal_wavenumber'
         - y 轴：频率，单位为 'cpd'
    lon_name : str | int, optional
        数据中的经度维度名称或索引, by default "longitude"
    time_name : str | int, optional
        数据中的时间维度名称或索引, by default "time"
    time_window : bool, optional
        是否给数据的时间维度上加窗, by default True
    time_window_alpha : float, optional
        加窗时使用的 Tukey 窗函数的 alpha 参数, by default 0.1
    lon_window : bool, optional
        是否给数据的经度维度上加窗, 建议非全球数据（不头尾循环）加窗。
        by default False
    lon_window_alpha : float, optional
        加窗时使用的 Tukey 窗函数的 alpha 参数, by default 0.1

    Returns
    -------
    xr.DataArray
        返回滤波后的数据，数据结构与输入 data 保持一致。

    """

    from scipy.signal.windows import tukey

    if not isinstance(data, xr.DataArray):
        raise TypeError("data must be an xarray.DataArray")

    # 计算时间与经度的采样间隔
    dt = data[time_name].values[1] - data[time_name].values[0]
    dt = np.timedelta64(dt, 's')
    ticks_in_day = np.timedelta64(1, 'D') / dt

    lon = data[lon_name].values
    zonal_res = lon[1] - lon[0]

    lon_axis = data.get_axis_num(lon_name)
    time_axis = data.get_axis_num(time_name)

    _data = data.values

    # 加窗
    if time_window:
        slices = [slice(None) if i == time_axis else None for i in range(_data.ndim)]
        _data = _data * tukey(_data.shape[time_axis], time_window_alpha)[*slices]

    if lon_window:
        slices = [slice(None) if i == lon_axis else None for i in range(_data.ndim)]
        _data = _data * tukey(_data.shape[lon_axis], lon_window_alpha)[*slices]

    # 计算频率坐标， x in zonal_wavenumber, y in cpd
    x_shift_freq = np.fft.fftfreq(data.shape[lon_axis], np.abs(zonal_res) / 360)
    x_shift_freq = np.fft.fftshift(x_shift_freq)
    y_shift_freq = np.fft.fftfreq(data.shape[time_axis], 1/ticks_in_day)
    y_shift_freq = np.fft.fftshift(y_shift_freq)

    result = _fft2_area_filter(_data, filter_area,
                               x_axes_index=lon_axis, y_axes_index=time_axis,
                                x_shift_freq=x_shift_freq,
                                y_shift_freq=y_shift_freq)

    attrs = data.attrs.copy()
    attrs.update({
        'filter': 'FFT time-longitude 2d filter',
        'filter_area': filter_area.attributes.to_json_str(None) \
            if isinstance(filter_area, FilterArea) else 'Polygon/MultiPolygon',
        'filter_time_window': str(time_window),
        'filter_time_window_alpha': time_window_alpha,
        'filter_lon_window': str(lon_window),
        'filter_lon_window_alpha': lon_window_alpha,
    })

    return xr.DataArray(result, dims=data.dims, coords=data.coords,
                        attrs=attrs, name=data.name)


def wk99_spectrum(data: xr.DataArray,
                  lon_name: str = "longitude", lat_name: str = "latitude",
                  time_name: str = "time",
                  window_days: int = 96, window_overlap_days: int = 64,
                  max_wavenumber: int = 50,) -> xr.Dataset:
    """计算 Wheeler-Kiladis 1999 的时空（频率-波数）谱。
    输入单个变量的三维数据（时间-纬度-经度），
    返回对称、非对称分量的功率谱、背景功率谱及其比值。

    参考：
        WHEELER M, KILADIS G N, 1999. Convectively Coupled Equatorial Waves:
        Analysis of Clouds and Temperature in the Wavenumber–Frequency Domain[J/OL].
        Journal of the Atmospheric Sciences, 56(3): 374-399.
        并参考了 NCL 的实现。

    Example
    -------
        >>> # 画出 OLR 数据的 WK99 频率-波数谱
        >>>
        >>> data = xr.open_dataset("olr.day.mean.nc").olr.sel(lat=slice(20, -20))
        >>> res = wk99_spectrum(data, 'lon', 'lat', 'time')
        >>> # 选择绘图范围
        >>> res = res.sel(wavenumber=slice(-20, 20), freq=slice(0, 1))
        >>>
        >>> fig = plt.figure(figsize=(8, 4))
        >>> for i in range(2):
        >>>     ax = fig.add_subplot(121 + i)
        >>>     d = res.spec_ratio.isel(type=i)
        >>>     ax.contourf(d.wavenumber, d.freq, np.log(d),
        ...                 cmap='RdBu_r', levels=np.linspace(-1, 1, 21),
        ...                 extend='both')
        >>> plt.show()



    Parameters
    ----------
    data : xr.DataArray
        输入用于计算的数据，必须为单层的三维数据，维度应包含时间、纬度、经度。
    lon_name, lat_name, time_name : str, optional
        DataArray 中经度、纬度、时间维度的名称,
        by default "longitude", "latitude", "time"
    window_days : int, optional
        循环窗口的天数, by default 96
    window_overlap_days : int, optional
        窗口间的重叠天数, by default 64
    max_wavenumber : int, optional
        输出的最大波数范围，单位为 zonal_wavenumber,

    Returns
    -------
    xr.DataSet
        返回一个包含了三个变量的数据集，分别为：

        - spec_origin: 原始的频率-波数谱，包含对称与非对称分量
        - spec_bg: 背景谱，由对称与非对称分量的平均值计算得到，并经过平滑处理
        - spec_ratio: 原始谱与背景谱的比值

    """
    from scipy.signal import windows, detrend
    from ._filter import fft_time_filter, smooth_121
    from ._base import unit
    from pandas import to_datetime

    # ====== 数据检查 =======

    # 必须为三维数据
    if data.ndim != 3:
        raise ValueError("data must be a 3D xarray.DataArray")

    # 必须不含 nan
    if np.any(np.isnan(data.values)):
        raise ValueError("input data contains NaN values, this is not allowed "
                         "in FFT calculation, please remove or fill NaN "
                         "values first.")

    # 输入的纬度需要对称
    latitudes = data[lat_name].values
    if np.max(latitudes) != -np.min(latitudes):
        raise ValueError("latitude values must be symmetric about the equator")

    zonal_res = np.abs(data[lon_name].values[1] - data[lon_name].values[0])

    time_start = to_datetime(data[time_name].values[0])
    time_end = to_datetime(data[time_name].values[-1])

    # =======================

    # 转为 时间、纬度、经度
    data = data.transpose(time_name, lat_name, lon_name)
    data = data.sortby(lat_name, ascending=False)
    _data = data.values

    dt = data[time_name].values[1] - data[time_name].values[0]
    dt = np.timedelta64(dt, 'ms').astype('int64')
    dt = dt / 1000  # 转为秒

    ticks_in_day = 86400 / dt

    window_length = int(window_days * ticks_in_day)
    window_overlap_length = int(window_overlap_days * ticks_in_day)
    total_days = data[time_name].size // ticks_in_day

    # detrend
    _data = detrend(_data, axis=0)

    # 如果时间长度大于1年，去除年信号
    if total_days >  365:
        _data = fft_time_filter(
            _data, 'highpass', 1/window_days * unit('cpd'),
            dt * unit('s'), axis=0
        )

    # 分离对称与非对称部分
    _data_north = _data[:, latitudes >= 0, :]
    _data_south = _data[:, latitudes <= 0, :][:, ::-1, :]  # 反转纬度顺序

    if _data_north.shape[1] != _data_south.shape[1]:
        raise ValueError("latitude dimension size mismatch after "
                         "separating northern and southern hemispheres")

    _data_sym = (_data_north + _data_south) / 2
    _data_asym = (_data_north - _data_south) / 2

    # 每个窗口循环
    steps = int(total_days // (window_days - window_overlap_days))
    window_window = windows.tukey(window_length, 0.1)[:, None, None]

    fft_result = np.zeros((2, window_length, _data.shape[2]))

    for step in range(steps):
        start_idx = step * (window_length - window_overlap_length)
        end_idx = start_idx + window_length

        if end_idx > data[time_name].size:
            break

        for i, _d in enumerate([_data_sym, _data_asym]):
            d = _d[start_idx:end_idx, :, :]

            # detrend
            d = detrend(d, axis=0)

            # 加窗
            d = d * window_window

            # 计算FFT
            fft_d = np.fft.fft2(d, axes=(0, 2))
            fft_d = np.fft.fftshift(fft_d, axes=(0, 2))
            fft_d = fft_d / fft_d.shape[0] / fft_d.shape[2] * 2
            fft_d = np.sum(fft_d, axis=1)
            fft_result[i] += np.abs(fft_d) ** 2

    fft_result = fft_result / steps
    fft_result = fft_result[:, ::-1, :]  # 反转时间维度

    freq = np.fft.fftshift(np.fft.fftfreq(window_length, d=1/ticks_in_day))
    wavenumber = np.fft.fftshift(np.fft.fftfreq(_data.shape[2], d=zonal_res/360))

    # 裁剪波数范围
    fft_result = fft_result[:, :, np.abs(wavenumber) <= max_wavenumber]
    wavenumber = wavenumber[np.abs(wavenumber) <= max_wavenumber]

    bg = np.mean(fft_result, axis=0)

    # smooth background
    for _ in range(10):
        bg = smooth_121(bg, axis=1)

    # 按照波数滤波：
    # 0~10: 10 次；10~20: 20 次；20~30: 30 次；>30: 40 次
    for i, k in enumerate(wavenumber):
        if np.abs(k) <= 10:
            n_smooth = 10
        elif np.abs(k) <= 20:
            n_smooth = 20
        elif np.abs(k) <= 30:
            n_smooth = 30
        else:
            n_smooth = 40

        for _ in range(n_smooth):
            bg[:, i] = smooth_121(bg[:, i], axis=0)

    # 构造输出数据

    coord_freq = xr.DataArray(
        freq, dims=('freq',), name='freq',
        coords={'freq': freq},
        attrs={
            'description': "frequency in cycles per day (cpd)",
            'long_name': "Frequency",
            'units': "1/day"
        }
    )
    coord_wavenumber = xr.DataArray(
        wavenumber, dims=('wavenumber',), name='wavenumber',
        coords={'wavenumber': wavenumber},
        attrs={
            'description': "zonal wavenumber at equator",
            'long_name': "Zonal Wavenumber",
            'units': "2.4953202e-08 / m"
        }
    )

    fft_result = xr.DataArray(
        fft_result, dims=('type', 'freq', 'wavenumber'), name='spec_origin',
        coords={
            'type': ['sym', 'asym'],
            'freq': coord_freq,
            'wavenumber': coord_wavenumber,
        },
        attrs={
            'description': "original frequency-wavenumber power spectrum of "
                           "symmetric and asymmetric components.",
            'long_name': "Original Spectrum",
        }
    )

    bg = xr.DataArray(
        bg, dims=('freq', 'wavenumber'), name='spec_bg',
        coords={
            'freq': coord_freq,
            'wavenumber': coord_wavenumber,
        },
        attrs={
            'description': "Background spectrum from average of symmetric "
                            "and asymmetric components, with smoothing applied.",
            'long_name': "Background Spectrum",
        }
    )

    ratio = xr.DataArray(
        fft_result.values / bg.values, dims=('type', 'freq', 'wavenumber'), name='spec_ratio',
        coords={
            'type': ['sym', 'asym'],
            'freq': coord_freq,
            'wavenumber': coord_wavenumber,
        },
        attrs={
            'description': "Ratio of original spectrum to background spectrum.",
            'long_name': "Ratio of original and background Spectrum",
        }
    )

    result = xr.Dataset({
        'spec_origin': fft_result,
        'spec_bg': bg,
        'spec_ratio': ratio,
    }, attrs={
        'description': f"wk99 frequency-wavenumber spectrum of variable {data.name}",
        "window_days": window_days,
        "window_overlap_days": window_overlap_days,
        "max_wavenumber": max_wavenumber,
        "window_number": steps,
        "time_range": f"{time_start} to {time_end}",
        "program": "mositen_ew.wk99_spectrum",
        "process_time": to_datetime('now').strftime("%Y-%m-%d %H:%M:%S"),
    })

    return result