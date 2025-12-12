import numpy as np
import moisten_ew as mew
import matplotlib.pyplot as plt

def test_enum():
    for wave in mew._BaseEW:
        print(f"{wave.name}, {wave.value}")
    for wave in mew.EquatorialWave:
        print(f"{wave.name}, {wave.value}, {mew._BaseEW.MRG in mew._BaseEW(wave.value)}")

def test_dimensionless_omega():
    fig = plt.figure(figsize=(8, 6))
    k = np.linspace(-10, 10, 100)
    waves = [
        mew.EquatorialWave.EASTWARD_MIXED_ROSSBY_GRAVITY_WAVE,
        mew.EquatorialWave.WESTWARD_MIXED_ROSSBY_GRAVITY_WAVE,
        mew.EquatorialWave.EASTWARD_INERTIO_GRAVITY_WAVE,
        mew.EquatorialWave.WESTWARD_INERTIO_GRAVITY_WAVE,
        mew.EquatorialWave.EQUATORIAL_ROSSBY_WAVE,
        mew.EquatorialWave.KELVIN_WAVE,
        mew.EquatorialWave.MRGW,
        mew.EquatorialWave.IGW,
    ]
    for wave in waves:
        omega = mew.angular_frequency_dimensionless(
            wave, k, n=2
        )
        plt.plot(k, omega.real, label=wave.name)

    plt.axhline(0, color='k', lw=0.5, ls='--')
    plt.axvline(0, color='k', lw=0.5, ls='--')
    plt.legend()
    plt.show()

def test_omega():
    fig = plt.figure(figsize=(8, 6))
    k = np.linspace(-20, 20, 200) * mew.unit('zonal_wavenumber')
    waves = [
        mew.EquatorialWave.EASTWARD_MIXED_ROSSBY_GRAVITY_WAVE,
        mew.EquatorialWave.WESTWARD_MIXED_ROSSBY_GRAVITY_WAVE,
        mew.EquatorialWave.EASTWARD_INERTIO_GRAVITY_WAVE,
        mew.EquatorialWave.WESTWARD_INERTIO_GRAVITY_WAVE,
        mew.EquatorialWave.EQUATORIAL_ROSSBY_WAVE,
        mew.EquatorialWave.KELVIN_WAVE,
        mew.EquatorialWave.MRGW,
        mew.EquatorialWave.IGW,
    ]
    for wave in waves:
        omega = mew.angular_frequency(
            wave, k,
        )
        plt.plot(k, omega.real/(2*np.pi), label=wave.name,
                 lw=3,  ls='--')

    plt.axhline(0, color='k', lw=0.5, ls='--')
    plt.axvline(0, color='k', lw=0.5, ls='--')
    plt.legend()
    plt.show()


def test_dist_dimensionless():
    x = np.linspace(-np.pi, np.pi, 30)
    y = np.linspace(-np.pi, np.pi, 30)
    waves = [
        mew.EquatorialWave.EASTWARD_MIXED_ROSSBY_GRAVITY_WAVE,
        mew.EquatorialWave.WESTWARD_MIXED_ROSSBY_GRAVITY_WAVE,
        mew.EquatorialWave.EASTWARD_INERTIO_GRAVITY_WAVE,
        mew.EquatorialWave.WESTWARD_INERTIO_GRAVITY_WAVE,
        mew.EquatorialWave.EQUATORIAL_ROSSBY_WAVE,
        mew.EquatorialWave.KELVIN_WAVE,
    ]

    fig = plt.figure(figsize=(16, 8))
    for i, wave in enumerate(waves):
        print(wave.name)
        u, v, h = mew.wave_distribution_dimensionless(
            wave, x, y, 0, 1, n=2
        )

        ax1 = fig.add_subplot(2, 3, i+1)
        ax1.contourf(x, y, h, levels=20, cmap='RdBu_r')
        ax1.quiver(x, y, u, v)
        ax1.set_title(wave.name, loc='left')
    plt.show()


def test_dist():
    x = np.linspace(-4000_000, 4000_000, 30) * mew.unit('m')
    y = np.linspace(-4000_000, 4000_000, 30) * mew.unit('m')
    waves = [
        mew.EquatorialWave.EASTWARD_MIXED_ROSSBY_GRAVITY_WAVE,
        mew.EquatorialWave.WESTWARD_MIXED_ROSSBY_GRAVITY_WAVE,
        mew.EquatorialWave.EASTWARD_INERTIO_GRAVITY_WAVE,
        mew.EquatorialWave.WESTWARD_INERTIO_GRAVITY_WAVE,
        mew.EquatorialWave.EQUATORIAL_ROSSBY_WAVE,
        mew.EquatorialWave.KELVIN_WAVE,
    ]

    fig = plt.figure(figsize=(16, 8))
    for i, wave in enumerate(waves):
        print(wave.name)
        u, v, h = mew.wave_distribution(
            wave, x, y, 0, 6*mew.unit('zonal_wavenumber'), n=1
        )

        ax1 = fig.add_subplot(2, 3, i+1)
        ax1.contourf(x, y, h, levels=20, cmap='RdBu_r')
        ax1.quiver(x, y, u, v)
        ax1.set_title(wave.name, loc='left')
    print(u.units, v.units, h.units)

    plt.show()

if __name__ == "__main__":
    # test_enum()
    # test_dimensionless_omega()
    # test_omega()
    # test_dist_dimensionless()
    test_dist()
