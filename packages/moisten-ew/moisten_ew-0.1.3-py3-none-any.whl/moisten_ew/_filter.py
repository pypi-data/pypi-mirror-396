import numpy as np
import xarray as xr
from typing import Literal
from ._base import unit, QuantityOrNum, _handle_quantity, quan2str, Q_
from scipy.signal.windows import tukey

def _axis_handle(data: xr.DataArray | np.ndarray,
                 axis: str | int) -> int:
    """获取数据某个维度的索引，可以是维度的索引值，也可以是维度的名称"""
    if isinstance(data, xr.DataArray):
        if isinstance(axis, str):
            axis = data.dims.index(axis)
    else:
        if isinstance(axis, str):
            raise ValueError("When data is a numpy array, axis must be an integer.")
    return axis

class _FilterFreqHandle:
    """处理滤波器参数输入"""

    def __init__(self, data: xr.DataArray | np.ndarray,
                btype: Literal['lowpass', 'highpass', 'bandpass', 'bandstop'],
                freq: QuantityOrNum | tuple[QuantityOrNum, QuantityOrNum],
                period: QuantityOrNum | tuple[QuantityOrNum, QuantityOrNum],
                sample_interval: QuantityOrNum,
                sample_freq: QuantityOrNum,
                axis: str | int
                ):

        if btype not in ['lowpass', 'highpass', 'bandpass', 'bandstop']:
            raise ValueError("filter_type must be one of 'lowpass', 'highpass', "
                            "'bandpass', 'bandstop'.")

        axis_index = _axis_handle(data, axis)

        # 频率 => low_freq, high_freq
        if freq is None and period is None:
            raise ValueError("Either frequency or period must be specified.")

        elif freq is not None and period is None:
            if isinstance(freq, (tuple, list, np.ndarray)):
                if btype in ['lowpass', 'highpass']:
                    raise ValueError("For lowpass and highpass filters, "
                                     "frequency must be a single value.")

                if len(freq) < 2:
                    raise ValueError("For bandpass and bandstop filters, "
                            "frequency must be a pair of (low_freq, high_freq).")

                low_freq = _handle_quantity(freq[0], 'cpd')
                high_freq = _handle_quantity(freq[1], 'cpd')
            else:
                if btype in ['bandpass', 'bandstop']:
                    raise ValueError("For bandpass and bandstop filters, "
                            "frequency must be a pair of (low_freq, high_freq).")
                low_freq = high_freq = _handle_quantity(freq, 'cpd')

        elif freq is None and period is not None:
            if isinstance(period, (tuple, list, np.ndarray)):
                if btype in ['lowpass', 'highpass']:
                    raise ValueError("For lowpass and highpass filters, "
                                     "period must be a single value.")

                if len(period) < 2:
                    raise ValueError("For bandpass and bandstop filters, "
                            "period must be a pair of (min_period, max_period).")

                low_period = _handle_quantity(period[0], 'day')
                high_period = _handle_quantity(period[1], 'day')
                low_freq = 1 / high_period
                high_freq = 1 / low_period
            else:
                if btype in ['bandpass', 'bandstop']:
                    raise ValueError("For bandpass and bandstop filters, "
                            "period must be a pair of (min_period, max_period).")
                period = _handle_quantity(period, 'day')
                low_freq = high_freq = 1 / period

        else:
            raise ValueError("can not specify both freq and period.")

        # 采样频率 => sample_freq, sample_interval
        if sample_interval is None and sample_freq is None:
            if isinstance(data, xr.DataArray):
                coord = data.coords[data.dims[axis_index]]
                dt = coord.values[1] - coord.values[0]
                dt = np.timedelta64(dt, 'ms').astype('int64')
                sample_interval = Q_(dt, 'ms').to('day')
                sample_freq = 1 / sample_interval
            else:
                raise ValueError("When data is a numpy array, "
                                 "sample_freq or sample_interval must be provided.")

        elif sample_interval is not None and sample_freq is None:
            sample_interval = _handle_quantity(sample_interval, 'day')
            sample_freq = 1 / sample_interval
        elif sample_interval is None and sample_freq is not None:
            sample_freq = _handle_quantity(sample_freq, 'cpd')
            sample_interval = 1 / sample_freq
        else:
            raise ValueError("can not specify both sample_freq and sample_interval.")

        if low_freq > high_freq:
            low_freq, high_freq = high_freq, low_freq

        self.low_freq = low_freq.to('cpd')
        self.high_freq = high_freq.to('cpd')
        self.sample_freq = sample_freq.to('cpd')
        self.sample_interval = sample_interval.to('day')
        self.axis_index = axis_index

        if low_freq != high_freq:
            self.freq_info = f"from {quan2str(low_freq)} to {quan2str(high_freq)}"
        else:
            self.freq_info = f"{quan2str(low_freq)}"


def fft_time_filter(data: xr.DataArray | np.ndarray,
               filter_type: Literal['lowpass', 'highpass', 'bandpass', 'bandstop'],
               freq: QuantityOrNum | tuple[QuantityOrNum, QuantityOrNum] = None,
               period: QuantityOrNum | tuple[QuantityOrNum, QuantityOrNum] = None,
               sample_interval: QuantityOrNum = None,
               sample_freq: QuantityOrNum = None,
               axis: str | int = 0,
               window: bool | float = 0.1
            ) -> xr.DataArray | np.ndarray:
    """使用 FFT 方法对时间序列数据进行滤波。指定的频率、采样间隔都可以带单位。

    Parameters
    ----------
    data : xr.DataArray | np.ndarray
        需要滤波的数据，可以是 xarray.DataArray 或 numpy.ndarray。
    filter_type : Literal['lowpass', 'highpass', 'bandpass', 'bandstop']
        过滤类型
    freq : QuantityOrNum | tuple[QuantityOrNum, QuantityOrNum]
        滤波的频率，如果输入为数字，则认为单位是 1/day (cpd)。

        - 对于低通滤波器（'lowpass'）和高通滤波器（'highpass'），输入单个频率值。
        - 对于带通滤波器（'bandpass'）和带阻滤波器（'bandstop'），
            输入频率范围的元组 (low_freq, high_freq)。
    sample_interval : QuantityOrNum, optional
        采样时间间隔，如果输入为数字，则认为单位是日。

        - 如果 data 是 xarray.DataArray 时，默认(sampling_interval=None)从坐标中
           自动计算该值；
        - 如果 data 是 numpy.ndarray，则必须提供该参数。
    axis : str | int, optional
        时间维度所在 axis，如果 data 是 xarray.DataArray 时，可以使用维度名称字符串
    window : bool | float, optional
        是否对时间序列数据应用 turky 窗函数以减少头尾偏差。

        - 如果为 False，则不应用窗函数；
        - 如果为 float，则表示 turky 窗函数的 alpha 参数，范围为 0 到 1 之间，
            默认为 0.1。

    Returns
    -------
    xr.DataArray | np.ndarray
        滤波后的数据，类型与输入 data 相同。

    """

    handle = _FilterFreqHandle(
        data, filter_type, freq, period,
        sample_interval, sample_freq, axis
    )
    low_freq = handle.low_freq
    high_freq = handle.high_freq
    sample_interval = handle.sample_interval
    axis_index = handle.axis_index


    fft_freq = np.fft.fftfreq(data.shape[axis_index], d=sample_interval.m)

    match filter_type:
        case 'lowpass':
            mask = np.abs(fft_freq) <= high_freq.m
        case 'highpass':
            mask = np.abs(fft_freq) >= low_freq.m
        case 'bandpass':
            mask = (np.abs(fft_freq) >= low_freq.m ) & \
                (np.abs(fft_freq) <= high_freq.m)
        case 'bandstop':
            mask = (np.abs(fft_freq) <= low_freq.m ) | \
                (np.abs(fft_freq) >= high_freq.m)

    mask_slice = [slice(None) if i == axis_index else None
                  for i in range(data.ndim)]
    mask = mask[*mask_slice]

    if isinstance(data, xr.DataArray):
        _data = data.values

        if window != False:
            slices = [slice(None) if i == axis_index else None
                      for i in range(data.ndim)]
            _data = _data * tukey(data.shape[axis_index], window)[*slices]

        data_fft = np.fft.fft(_data, axis=axis_index)
        data_filtered = np.fft.ifft(data_fft * mask, axis=axis_index).real

        result = xr.DataArray(data_filtered, name=data.name, dims=data.dims,
                                coords=data.coords, attrs=data.attrs)
        result = result.assign_attrs({
            'filter': 'fft_time_filter',
            'filter_type': filter_type,
            'filter_frequency': handle.freq_info,
            'filter_sample_interval': quan2str(sample_interval),
        })
        return result
    else:
        if window != False:
            slices = [slice(None) if i == axis_index else None
                      for i in range(data.ndim)]
            _data = data * tukey(data.shape[axis_index], window)[*slices]
        else:
            _data = data

        data_fft = np.fft.fft(_data, axis=axis_index)
        data_filtered = np.fft.ifft(data_fft * mask, axis=axis_index).real
        return data_filtered


def smooth_121(data: np.ndarray, axis: int = 0) -> np.ndarray:
    """对数据进行 1-2-1 平滑处理。

    Parameters
    ----------
    data : np.ndarray
        需要平滑处理的数据。
    axis : int, optional
        处理维度, by default 0

    Returns
    -------
    np.ndarray
        平滑处理后的数据。
    """
    from scipy.signal import convolve
    kernel = np.array([1, 2, 1]) / 4
    shape = [1] * data.ndim
    shape[axis] = 3
    kernel = kernel.reshape(shape)

    return convolve(data, kernel, mode='same', method='auto')



def _butter(data: np.ndarray, T: float|tuple[float, float], fs: int,
            btype: Literal['lowpass', 'highpass', 'bandpass', 'bandstop'],
            axis: int = 0, N: int = 3,) -> np.ndarray:
    """巴特沃斯滤波器时间周期转换"""
    import scipy.signal as signal

    if btype in ['lowpass', 'highpass']:
        Wn = 2/(T*fs)
    elif btype in ['bandpass', 'bandstop']:
        Wn = (2/(T[1]*fs), 2/(T[0]*fs))
    else:
        raise ValueError("ftype参数错误, "
                "有效值为 'lowpass', 'highpass', 'bandpass', 'bandstop'")

    b, a = signal.butter(N, Wn, btype)
    return signal.filtfilt(b, a, data, axis=axis)


def _get_axis(data: xr.DataArray, axis: int | str) -> int:
    """获取数据某个维度的索引，可以是维度的索引值，也可以是维度的名称"""
    if isinstance(axis, str):
        axis = data.dims.index(axis)
    return axis


def butter_filter(data: xr.DataArray | np.ndarray,
        btype: Literal['lowpass', 'highpass', 'bandpass', 'bandstop'],
        freq: QuantityOrNum | tuple[QuantityOrNum, QuantityOrNum] = None,
        period: QuantityOrNum | tuple[QuantityOrNum, QuantityOrNum] = None,
        sample_freq: QuantityOrNum = None,
        sample_interval: QuantityOrNum = None,
        axis: int | str = 0, N: int = 3,) -> xr.DataArray | np.ndarray:
    """使用 Butterworth 滤波器过滤数据。推荐各个参数都带单位，避免单位转换造成的问题。

    滤波的范围可以用 `freq` 参数指定频率，或用 `period` 参数指定周期，必须指定其中一个。
    若滤波器类型为 'lowpass' 或 'highpass'，则只需指定单个值；
    若滤波器类型为 'bandpass' 或 'bandstop'，则需指定一对值 (min, max)。

    同样，参数 `sample_freq` 与 `sample_interval` 为数据的采样频率或采样间隔，
    如果数据为 xarray.DataArray 时，可以不指定，程序会自动从坐标中计算该值，
    否则必须指定其中一个。

    Example
    -------
        >>> data = xr.open_dataarray('data.nc') # ('time', 'lat', 'lon')
        >>>
        >>> # 5~10 日周期带通滤波（不带单位）
        >>> butter_filter(data, 'bandpass', period=(5, 10), axis='time')
        >>>
        >>> # 30 日低通滤波（带单位，数据为1日4次）
        >>> from mositen_ew import unit
        >>> butter_filter(data, 'lowpass', period=30 * unit('day'),
        ...               sample_interval=0.25 * unit('day'), axis='time')

    Parameters
    ----------
    data : xr.DataArray | np.ndarray
        需要滤波的数据。
    btype : Literal['lowpass', 'highpass', 'bandpass', 'bandstop']
        滤波器类型
    freq : QuantityOrNum | tuple[QuantityOrNum, QuantityOrNum], optional
        滤波过滤的频率，若无单位则认为是 1/day (cpd)， by default None
    period : QuantityOrNum | tuple[QuantityOrNum, QuantityOrNum], optional
        滤波过滤的周期，若无单位则认为是 day (天)， by default None
    sample_freq : QuantityOrNum, optional
        数据的采样频率，若无单位则认为是 1/day (cpd)， by default None
    sample_interval : QuantityOrNum, optional
        数据的采样间隔，若无单位则认为是 day (天)， by default None
    axis : int | str, optional
        滤波的轴，如果 data 是 xarray.DataArray 时，可以使用维度名称字符串。
    N : int, optional
        巴特沃斯滤波器的阶数, by default 3

    Returns
    -------
    xr.DataArray | np.ndarray
        滤波后的数据，类型与输入 data 相同。

    """

    handle = _FilterFreqHandle(
        data, btype, freq, period,
        sample_interval, sample_freq, axis
    )
    p_min = 1 / handle.high_freq
    p_max = 1 / handle.low_freq
    sample_freq = handle.sample_freq
    axis = handle.axis_index

    # 滤波参数
    T = (p_min.m, p_max.m) if btype in ['bandpass', 'bandstop'] else p_max.m
    fs = sample_freq.m

    # 滤波
    if isinstance(data, xr.DataArray):
        axis = _get_axis(data, axis)
        filtered_data = _butter(data.values, T, fs, btype, axis, N)
        attrs = data.attrs.copy()
        attrs.update({
            'filter': 'Butterworth Filter',
            'filter_type': btype,
            'filter_period': (f"from {quan2str(p_min)} to {quan2str(p_max)}"
                              if btype in ['bandpass', 'bandstop']
                              else f"at {quan2str(p_max)}"),
            'filter_sample_frequency': quan2str(sample_freq),
        })
        return xr.DataArray(filtered_data,
                            name=data.name, dims=data.dims,
                            coords=data.coords, attrs=attrs)
    else:
        return _butter(data, T, fs, btype, axis, N)

