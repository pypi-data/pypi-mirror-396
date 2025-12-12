import numpy as np
import moisten_ew as mew
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
import xarray as xr

def plot_area(areas: mew.FilterArea | list[mew.FilterArea]):
    if isinstance(areas, mew.FilterArea):
        areas = [areas]

    fig = plt.figure(figsize=(8, 6))

    for area in areas:
        if isinstance(area.shape, MultiPolygon):
            for poly in area.shape.geoms:
                x, y = poly.exterior.xy
                plt.plot(x, y)
                plt.scatter(x, y, c='r', s=10)
        else:
            x, y = area.shape.exterior.xy
            plt.plot(x, y)
            plt.scatter(x, y, c='r', s=10)
    plt.xlabel('Zonal Wavenumber')
    plt.ylabel('Frequency (cpd)')
    plt.title(area.attributes.name)
    plt.grid()
    plt.show()

def test_rect_area():
    a = mew.RectangleFilterArea(-10, 10, 0.1, 0.5)
    print(a.attributes.to_json_str())
    # plot
    plot_area(a)

def test_kelvin_area():
    a = mew.KelvinFilterZone()
    print(a.attributes.to_json_str())
    plot_area(a)

def test_operation():
    a = mew.RectangleFilterArea(-10, 10, 0.1, 0.5)
    b = mew.KelvinFilterZone()
    c = mew.RectangleFilterArea(5, 10, 0.1, 0.2)
    d = mew.RectangleFilterArea(15, 20, 0.1, 0.2)

    a1 = a.intersection(b).difference(c).union(d)
    print(a1.attributes.to_json_str())
    plot_area([a1])

def test_mask():
    x = np.linspace(-20, 20, 101)
    y = np.linspace(-20, 20, 51)
    area = mew.RectangleFilterArea(3, 8, 2, 4)
    area2 = mew.RectangleFilterArea(5, 9, 5, 8)
    mask = mew._get_fft_mask(x, y, area.union(area2).shape)
    plt.pcolormesh(x, y, mask,)
    plt.plot(area.shape.exterior.xy[0], area.shape.exterior.xy[1], c='r')
    plt.plot(area2.shape.exterior.xy[0], area2.shape.exterior.xy[1], c='r')
    plt.colorbar()
    plt.show()


def test_fft2_area_filter():
    # 构造测试数据
    data = np.random.rand(20, 120, 150)

    # 构造滤波区域
    filter_area = mew.RectangleFilterArea(0.1, 0.2, 0.1, 0.25)

    # 执行二维FFT区域滤波
    filtered_data = mew._fft2_area_filter(
        data,
        filter_area,
        y_axes_index=0
    )

    plt.pcolormesh(filtered_data[:, 0, :], cmap='viridis')
    plt.colorbar(label='Filtered Amplitude')
    plt.show()


def test_mrg_area():
    a = mew.MRGFilterArea(max_wavenumber=10,
                          max_freq=0.8)
    plot_area(a)

def test_er_area():
    a = mew.ERFilterArea()
    plot_area(a)

def test_ig_area():
    a = mew.IGFilterArea(max_wavenumber=15)
    plot_area(a)


def test_all_area():
    fig = plt.figure(figsize=(10, 8))
    areas = [
        mew.KelvinFilterArea(),
        mew.MRGFilterArea(),
        mew.ERFilterArea(),
        mew.IGFilterArea(),
        mew.MJOFilterArea(),
        mew.TDFilterArea(),
        mew.EllipseFilterArea(3, 0.5, 2, 0.1)
    ]
    for area in areas:
        x, y = area.shape.exterior.xy
        plt.plot(x, y, label=area.attributes.name)
    plt.xlabel('Zonal Wavenumber')
    plt.ylabel('Frequency (cpd)')
    plt.legend()
    plt.show()


def test_fft_filter():
    data = xr.open_dataarray('test/test_data/v.200011.nc').sel(
        latitude=0, pressure_level=850
    ).load()

    area = mew.MRGFilterArea()
    area = area.union(mew.KelvinFilterArea())

    filter_data = mew.fft_time_lon_area_filter(
        data, area,
        time_name='valid_time', lon_name='longitude'
    )
    print(filter_data.attrs['filter_area'])

    plt.pcolormesh(filter_data.longitude, filter_data.valid_time, filter_data,
                   cmap='jet')
    plt.colorbar(label='Filtered Amplitude')
    plt.show()


def test_121():
    from moisten_ew._filter import smooth_121

    a = np.ones((10, 11))

    a = smooth_121(a, axis=1)
    print(a)
    print(a.shape)


def test_wk99():
    from moisten_ew._fft import wk99_spectrum
    data = xr.open_dataset("/Users/toyohay/Documents/equator_waves/data/olr.day.mean.nc").olr.sel(
        lat=slice(20, -20),
        time=slice("2000", None)
    )

    res = wk99_spectrum(data, 'lon', 'lat', 'time')
    res = res.sel(wavenumber=slice(-20, 20), freq=slice(0, 1))

    fig = plt.figure(figsize=(8, 6))
    for i in range(2):
        ax = fig.add_subplot(121 + i)
        d = res.spec_ratio.isel(type=i)
        ax.contourf(d.wavenumber, d.freq, np.log(d),
                      cmap='RdBu_r', levels=np.linspace(-1, 1, 21),
                      extend='both')
    plt.show()


def test_butter():
    
    data = xr.open_dataarray('test/test_data/v.200011.nc').sel(
        latitude=0, pressure_level=850
    ).load()
    from moisten_ew._filter import butter_filter

    res = butter_filter(
        data, 'bandpass', period=(3, 8),
        axis='valid_time'
    )

    plt.pcolormesh(res.longitude, res.valid_time, res,
                   cmap='jet')
    plt.colorbar(label='Filtered Amplitude')
    plt.show()



if __name__ == "__main__":
    # test_rect_area()
    # test_kelvin_area()
    # test_operation()
    # test_mask()
    # test_fft2_area_filter()
    # test_er_area()
    # test_ig_area()
    # test_mrg_area()
    # test_all_area()
    # test_fft_filter()


    # test_121()
    # test_wk99()
    test_butter()