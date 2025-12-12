import numpy as np
import moisten_ew as mew
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
from moisten_ew._filter import fft_time_filter


def test_fft_time_filter():
    time = pd.date_range('2000-01-01', periods=200, freq='1h')
    t = np.arange(len(time))
    v1 = np.sin(2 * np.pi * t / 24 * 0.35)
    v2 = np.sin(2 * np.pi * t / 24 * 1.1)
    v3 = np.sin(2 * np.pi * t / 24 * 2.3)
    v = v1 + v2 + v3
    data = xr.DataArray(v, coords=[time], dims=['time'])

    filtered = fft_time_filter(
        data, 'highpass', 1.5
    )

    plt.figure(figsize=(10, 6))
    for v in [v1, v2, v3]:
        plt.plot(data.time, v, label='Original', lw=1)

    plt.plot(data.time, v1+v2+v3, label='Original', lw=1)
    plt.plot(filtered.time, filtered, label='Filtered', lw=1, c='k')
    plt.legend()
    plt.show()



if __name__ == "__main__":
    test_fft_time_filter()