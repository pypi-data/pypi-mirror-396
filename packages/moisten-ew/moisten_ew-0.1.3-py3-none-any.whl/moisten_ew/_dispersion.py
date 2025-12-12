import numpy as np
from enum import Enum
from ._base import (EquatorialWave, PI, EARTH_GRAVITY, _BaseEW,
                    ROSSBY_PARAMETER_ON_EQUATOR, _handle_quantity)
from pint import Quantity


def angular_frequency_dimensionless(wave: EquatorialWave,
                                    wavenumber: np.ndarray,
                                    n: int=1, keep_direction: bool=True,
                                    ) -> np.ndarray:
    """计算无量纲化(Matsuno, 1966)下赤道波动的角频率(ω)，可用于绘制频散曲线或计算。
    使用现代流行标准，以波数的正负表示波动相速度的方向，角频率 ω >= 0。

    Parameters
    ----------
    wave : EquatorialWave
        赤道波动类型
    wavenumber : np.ndarray
        无量纲经向波数 (k)
    n : int, optional
        埃尔米特多项式的阶数 n, 若为 MRG 波或 Kelvin 波，此参数无效，默认为 1。
    keep_direction : bool, optional
        是否只保留波动的传播方向的值，未指定方向的波动此参数无效。默认为 True。
        例如如果为 True，则对于东传波，传入的负波数对应的频率将被设为 NaN；

    Returns
    -------
    np.ndarray
        该波动无量纲下的角频率 ω
    """

    k = -wavenumber
    base_type = _BaseEW(wave.value)
    result = None

    # MRG wave
    if _BaseEW.MRG in base_type:
        result = np.sqrt(k**2/4 + 1) - k/2

    # Kelvin wave
    elif _BaseEW.KELVIN in base_type:
        result = -k

    else:
        # 转为复数计算
        k = np.asarray(k, dtype=np.complex64)
        p = -(k**2 + 2*n + 1)
        q = k
        o = (-1+3**(1/2)*1j)/2

        # Other waves
        if _BaseEW.IG in base_type:
            result = (-q/2+((q/2)**2+(p/3)**3)**(1/2))**(1/3) +\
                    (-q/2-((q/2)**2+(p/3)**3)**(1/2))**(1/3)

        elif _BaseEW.ROSSBY in base_type:
            result = o**2 * (-q/2+((q/2)**2+(p/3)**3)**(1/2))**(1/3) +\
                    o * (-q/2-((q/2)**2+(p/3)**3)**(1/2))**(1/3)

        if result is None:
            raise ValueError(f"Invalid wave type: {wave}")

    result = result.real

    if keep_direction:
        result = result.astype(np.float64)
        if _BaseEW.EASTWARD in base_type:
            result[k > 0] = np.nan
        elif _BaseEW.WESTWARD in base_type:
            result[k < 0] = np.nan

    return result


def angular_frequency(wave: EquatorialWave,
                      wavenumber: Quantity | np.ndarray | float,
                      n: int=1,
                      equivalent_depth: Quantity|float=25,
                      g: Quantity=EARTH_GRAVITY,
                      beta: Quantity=ROSSBY_PARAMETER_ON_EQUATOR) -> Quantity:
    """计算有量纲的赤道波动角频率(ω)，返回的角频率单位为 rad/day。
    使用现代流行标准，以波数的正负表示波动相速度的方向，角频率 ω >= 0。

        >>> import numpy as np
        >>> import mositen_ew as mew
        >>>
        >>> # 定义带单位波数
        >>> k = np.linspace(-20, 20, 200) * mew.unit('zonal_wavenumber')
        >>> omega = mew.angular_frequency(mew.EquatorialWave.KELVIN_WAVE, k)
        >>> freq = omega/(2*np.pi) # from rad/day to 1/day

    Parameters
    ----------
    wave : EquatorialWave
        赤道波动类型
    wavenumber : Quantity | np.ndarray | float
        带单位的波数，推荐使用单位 'zonal_wavenumber'，如果输入不带单位，则认为是 '1/m'。
    n : int, optional
        埃尔米特多项式的阶数 n, 若为 MRG 波或 Kelvin 波，此参数无效，默认为 1。
    equivalent_depth : Quantity | float, optional
        等效深度，默认为 25
    g : Quantity, optional
        重力加速度, 默认为地表重力加速度 EARTH_GRAVITY
    beta : Quantity, optional
        赤道上的 β 参数, 默认为 ROSSBY_PARAMETER_ON_EQUATOR

    Returns
    -------
    Quantity
        该波动有量纲下的角频率 ω，单位为 rad/day

    """

    # 把 k 转为波数（个/米）
    k = _handle_quantity(wavenumber, '1/m')

    # 转为相位/米的波数
    k = k * 2 * PI # rad/m

    # 处理常数
    H = _handle_quantity(equivalent_depth, 'm')
    g = _handle_quantity(g, 'm/s**2')
    beta = _handle_quantity(beta, '1/(m*s)')

    # 重力波速度
    c = np.sqrt(g*H)

    # 转换到无量纲计算
    k = k * np.sqrt(c / beta)

    omega = angular_frequency_dimensionless(
        wave, k.m, n=n, keep_direction=True,
    )

    # 转换回有量纲
    omega *= np.sqrt(c*beta)
    omega = omega.to('rad/day')

    return omega



def _dist_dimensionless(x: np.ndarray, y: np.ndarray, t: float,
                        k: float, omega: float, n:int=1
                        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    from scipy.special import hermite

    if x.ndim == 1 and y.ndim == 1:
        x, y = np.meshgrid(x, y)
    elif x.ndim == 2 and y.ndim == 2:
        pass
    else:
        raise ValueError("x and y must both be 1D or 2D arrays.")

    ey = np.exp(-y**2/2)
    if n >= 1:
        v = -(omega**2-k**2) * ey * hermite(n, True)(y) * np.sin(k*x + omega*t)
        u = ey * (0.5 * (omega - k) * hermite(n+1, True)(y) + n*(omega + k) *\
                   hermite(n-1, True)(y)) * np.cos(k*x + omega*t)
        phi = ey * (0.5 * (omega - k) * hermite(n+1, True)(y) - n*(omega + k) *\
                     hermite(n-1, True)(y)) * np.cos(k*x + omega*t)
    elif n == 0:
        v = -2 * (omega+k) * ey * np.sin(k*x + omega*t)
        u = 2 * y * ey * np.cos(k*x + omega*t)
        phi = 2 * y * ey * np.cos(k*x + omega*t)
    elif n == -1:
        v = np.zeros_like(x)
        u = ey * np.cos(k*x + omega*t)
        phi = ey * np.cos(k*x + omega*t)
    else:
        raise ValueError("n must be >= -1")

    return u, v, phi


def wave_distribution_dimensionless(wave: EquatorialWave,
                                x: np.ndarray, y: np.ndarray, t: float,
                                wavenumber: np.ndarray | float, n: int=1,
                                ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """计算无量纲化下赤道波动的变量场分布，返回 x, y 网格上的 (u, v, φ) 分布。

    Parameters
    ----------
    wave : EquatorialWave
        赤道波动类型
    x : np.ndarray
        无量纲经向坐标
    y : np.ndarray
        无量纲纬向坐标
    t : float
        无量纲时间
    wavenumber : np.ndarray | float
        无量纲经向波数
    n : int, optional
        埃尔米特多项式的阶数 n, 若为 MRG 波或 Kelvin 波，此参数无效，默认为 1。

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        返回扰动场的 (u, v, φ) 分布

    """

    base_type = _BaseEW(wave.value)

    if _BaseEW.EASTWARD in base_type:
        k = np.abs(wavenumber)
    elif _BaseEW.WESTWARD in base_type:
        k = -np.abs(wavenumber)
    else:
        raise ValueError("Wave type must specify direction (eastward or westward).")



    if _BaseEW.MRG in base_type:
        n = 0
    elif _BaseEW.KELVIN in base_type:
        n = -1

    omega = angular_frequency_dimensionless(
        wave, np.array([k]), n=n,
    )[0]

    if _BaseEW.MRG in base_type or _BaseEW.IG in base_type: # 不知道为什么需要反号
        k = -k

    u, v, phi = _dist_dimensionless(x, y, t, k, omega, n=n)

    return u, v, phi


def wave_distribution(wave: EquatorialWave,
                    x: Quantity | np.ndarray,
                    y: Quantity | np.ndarray,
                    t: Quantity | float,
                    wavenumber: Quantity | float,
                    n: int=1,
                    equivalent_depth: Quantity|float=25,
                    g: Quantity=EARTH_GRAVITY,
                    beta: Quantity=ROSSBY_PARAMETER_ON_EQUATOR
                    ) -> tuple[Quantity, Quantity, Quantity]:
    """计算有量纲下赤道波动的变量场分布，返回 x, y 网格上的 (u, v, φ) 分布。
    x, y 坐标数组，需要都是一维或都是二维数组。

    Parameters
    ----------
    wave : EquatorialWave
        赤道波动类型
    x : Quantity | np.ndarray
        带单位的经向坐标数组，如果输入不带单位，则认为是 'm'。
    y : Quantity | np.ndarray
        带单位的纬向坐标数组，如果输入不带单位，则认为是 'm'。
    t : Quantity | float
        带单位的时间，推荐使用单位 's'，如果输入不带单位，则认为是 's'。
    wavenumber : Quantity | float
        带单位的波数，推荐使用单位 'zonal_wavenumber'，如果输入不带单位，则认为是 '1/m'。
    n : int, optional
        埃尔米特多项式的阶数 n, 若为 MRG 波或 Kelvin 波，此参数无效，默认为 1。
    equivalent_depth : Quantity | float, optional
        等效深度，默认为 25，单位为 'm'。
    g : Quantity, optional
        重力加速度, 默认为地表重力加速度 EARTH_GRAVITY
    beta : Quantity, optional
        赤道上的 β 参数, 默认为 ROSSBY_PARAMETER_ON_EQUATOR

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        返回扰动场的 (u, v, φ) 分布

    """

    # 处理坐标和时间的单位
    x = _handle_quantity(x, 'm')
    y = _handle_quantity(y, 'm')
    t = _handle_quantity(t, 's')

    # 把 k 转为波数（个/米）
    k = _handle_quantity(wavenumber, '1/m')

    # 转为相位/米的波数
    k = k * 2 * PI # rad/m

    # 处理常数
    H = _handle_quantity(equivalent_depth, 'm')
    g = _handle_quantity(g, 'm/s**2')
    beta = _handle_quantity(beta, '1/(m*s)')

    # 重力波速度
    c = np.sqrt(g*H)

    # 转换到无量纲计算
    k = k * np.sqrt(c / beta)
    x = x * np.sqrt(beta / c)
    y = y * np.sqrt(beta / c)
    t = t * np.sqrt(c * beta)

    u, v, phi = wave_distribution_dimensionless(
        wave, x.m, y.m, t.m, k.m, n=n,
    )

    # 转换回有量纲
    u = u * c
    v = v * c
    phi = phi * c**2

    return u, v, phi