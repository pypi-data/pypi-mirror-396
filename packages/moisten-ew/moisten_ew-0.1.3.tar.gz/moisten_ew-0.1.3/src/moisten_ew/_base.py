from enum import Enum, auto, Flag
from pint import UnitRegistry
from numpy import ndarray
from pint import Quantity

class _BaseEW(Flag):
    """基本赤道波动类型的标识，用于组合不同方向的波动类型。"""
    KELVIN = auto()
    """Kelvin wave"""
    IG = auto()
    """Inertio-Gravity wave"""
    ROSSBY = auto()
    """Equatorial Rossby wave"""
    MRG = auto()
    """Mixed Rossby-Gravity wave"""
    EASTWARD = auto()
    """Eastward wave"""
    WESTWARD = auto()
    """Westward wave"""


class EquatorialWave(Enum):
    """
    不同类型的赤道波动的枚举类，用于波动类型的标识与选择。
    包含全称与缩写两种表示方式。

    The enumeration class for different types of equatorial waves,
    used for wave type identification and selection.
    It includes both full names and abbreviations.

    """
    # Full names
    KELVIN_WAVE = _BaseEW.KELVIN | _BaseEW.EASTWARD
    "Kelvin Wave"

    EASTWARD_INERTIO_GRAVITY_WAVE = _BaseEW.IG | _BaseEW.EASTWARD
    "Eastward Inertio-Gravity Wave, n > 0"

    WESTWARD_INERTIO_GRAVITY_WAVE = _BaseEW.IG | _BaseEW.WESTWARD
    "Westward Inertio-Gravity Wave, n > 0"

    INERTIO_GRAVITY_WAVE = _BaseEW.IG
    "Inertio-Gravity Wave (both eastward and westward), n > 0"

    EQUATORIAL_ROSSBY_WAVE = _BaseEW.ROSSBY | _BaseEW.WESTWARD
    "Equatorial Rossby Wave, n > 0"

    WESTWARD_MIXED_ROSSBY_GRAVITY_WAVE = _BaseEW.MRG | _BaseEW.WESTWARD
    "Westward Mixed Rossby-Gravity Wave, n = 0"

    EASTWARD_MIXED_ROSSBY_GRAVITY_WAVE = _BaseEW.MRG | _BaseEW.EASTWARD
    "Eastward Mixed Rossby-Gravity Wave, n = 0"

    MIXED_ROSSBY_GRAVITY_WAVE = _BaseEW.MRG
    "Mixed Rossby-Gravity Wave (both eastward and westward), n = 0"

    # Abbr
    KW = KELVIN_WAVE
    "Kelvin Wave"

    EIGW = EASTWARD_INERTIO_GRAVITY_WAVE
    "Eastward Inertio-Gravity Wave, n > 0"

    WIGW = WESTWARD_INERTIO_GRAVITY_WAVE
    "Westward Inertio-Gravity Wave, n > 0"

    IGW = INERTIO_GRAVITY_WAVE
    "Inertio-Gravity Wave (both eastward and westward), n > 0"

    ERW = EQUATORIAL_ROSSBY_WAVE
    "Equatorial Rossby Wave, n > 0"

    WMRGW = WESTWARD_MIXED_ROSSBY_GRAVITY_WAVE
    "Westward Mixed Rossby-Gravity Wave, n = 0"

    EMRGW = EASTWARD_MIXED_ROSSBY_GRAVITY_WAVE
    "Eastward Mixed Rossby-Gravity Wave, n = 0"

    MRGW = MIXED_ROSSBY_GRAVITY_WAVE
    "Mixed Rossby-Gravity Wave (both eastward and westward), n = 0"


# ========= 单位相关 =========

unit = UnitRegistry()
unit.define('zonal_wavenumber = 2.4953202e-08 / m')
unit.define('cpd = 1 / day')

QuantityOrNum = Quantity | float | int
"""一个数字或带单位的数字"""


def Q_(value, units=None):
    """Create a Quantity with the given value and units."""
    return unit.Quantity(value, units)


def quan2str(value: Quantity) -> str:
    """将带单位的数值转换为字符串表示"""
    return f"{value.magnitude:g} {value.units}"

# 常量

PI = Q_(3.141592653589793, 'rad')
"""圆周率"""

# 地球形状参数，来自于 WGS-84 https://en.wikipedia.org/wiki/World_Geodetic_System

EARTH_MAJOR_AXIS = Q_(6378137.0, 'm')
"""地球长半轴 """

EARTH_MINOR_AXIS = Q_(6356752.314245, 'm')
"""地球短半轴 """

EARTH_RADIUS = EARTH_MAJOR_AXIS
"""地球半径（长半轴） """

# 地球物理常量
EARTH_GRAVITY = Q_(9.80665, 'm/s**2')
"""标准重力加速度 https://en.wikipedia.org/wiki/Gravity_of_Earth"""

SOLAR_DAY = Q_(86400, 's')
"""太阳日"""

SIDEREAL_DAY = Q_(86164.0905, 's')
"""恒星日 https://en.wikipedia.org/wiki/Sidereal_time"""

EARTH_ROTATION_ANGULAR_VELOCITY = 2 * PI / SIDEREAL_DAY
"""地球自转角速度 Omega"""

ROSSBY_PARAMETER_ON_EQUATOR = 2 * EARTH_ROTATION_ANGULAR_VELOCITY / EARTH_RADIUS
"""赤道上的罗斯贝参数"""

EARTH_EQUATOR_LENGTH = Q_(2 * PI * EARTH_RADIUS, 'm')
"""地球赤道长度"""

LENGTH_PRE_LATITUDE = EARTH_EQUATOR_LENGTH / 360
"""一度纬度的长度"""

def _handle_quantity(value: Quantity | ndarray | float | int, units: str) -> Quantity:
    """处理输入的值，如果没有单位，则加上 unit，如果有单位，则转换为 unit。
    """
    if isinstance(value, (int, float, ndarray)):
        value = Q_(value, unit(units))
    elif not isinstance(value, Quantity):
        raise TypeError("input value must be a Quantity, ndarray or float")
    return value.to(units)