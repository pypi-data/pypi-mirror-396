"""
========================
FFT滤波区域相关。
所有的滤波区域的坐标单位均为：

 - x 轴：纬向波数，单位为 'zonal_wavenumber'
 - y 轴：频率，单位为 'cpd'
------------------------
Author: Lilidream
Date: 2025-11-13
========================
"""

from shapely import Polygon, MultiPolygon
from ._base import (
    unit, Quantity, _handle_quantity, EquatorialWave,
    EARTH_GRAVITY, ROSSBY_PARAMETER_ON_EQUATOR, PI,
    QuantityOrNum
)
from dataclasses import dataclass, field
import numpy as np
import json

@dataclass
class FilterAreaAttributes:
    """滤波区域的属性信息类，用于描述滤波区域的元数据。"""
    name: str
    description: str = ""
    parameters: dict[str, QuantityOrNum] = field(default_factory=lambda: {})
    is_exclusive: bool = False
    union_from: list['FilterAreaAttributes'] = field(default_factory=list)
    intersection_from: list['FilterAreaAttributes'] = field(default_factory=list)
    different: dict[str, 'FilterAreaAttributes'] = field(default_factory=lambda: {})

    @staticmethod
    def _convert_value(value: QuantityOrNum) -> str:
        """转换数值为字符串表示"""
        if isinstance(value, Quantity):
            return f"{value.magnitude:g} {value.units}"
        else:
            return f"{value:g}"

    def asdict(self) -> dict:
        data = {
            "name": self.name,
        }
        if len(self.description) > 0:
            data["description"] = self.description
        if len(self.parameters) > 0:
            data["parameters"] = {k: self._convert_value(v) for k, v in self.parameters.items()}
        if self.is_exclusive:
            data["is_exclusive"] = self.is_exclusive
        if len(self.union_from) > 0:
            data["union_from"] = [attr.asdict() for attr in self.union_from]
        if len(self.intersection_from) > 0:
            data["intersection_from"] = [attr.asdict() for attr in self.intersection_from]
        if len(self.different) > 0:
            data["different"] = {k: v.asdict() for k, v in self.different.items()}

        return data

    def to_json_str(self, indent=2) -> str:
        """将属性转换为 JSON 字符串"""
        return json.dumps(self.asdict(), ensure_ascii=False, indent=indent)


class FilterArea:
    """用于表示FFT滤波区域的类，包含滤波区域的几何形状和属性信息。"""
    def __init__(self, shape: Polygon | MultiPolygon, attributes: FilterAreaAttributes):
        """给定滤波区域的多边形范围与属性，创建一个滤波区域实例。

        区域多边形的坐标分别为：

         - x 轴：纬向波数，单位为 'zonal_wavenumber'
         - y 轴：频率，单位为 'cpd'

        Parameters
        ----------
        shape : Polygon | MultiPolygon
            滤波区域的几何形状
        attributes : FilterAreaAttributes
            滤波区域的属性信息，将作为描述滤波结果的元数据
        """
        self.shape = shape
        """区域的形状"""

        self.attributes = attributes
        """区域的属性信息"""


    @staticmethod
    def to_cpd(val: float) -> float:
        """将频率从 meter * zonal_wavenumber / second 转为 cpd"""
        return val * 2.4953202e-08 * 86400


    def _clip_by_rectangle(self, left: QuantityOrNum, right: QuantityOrNum,
                          bottom: QuantityOrNum, top: QuantityOrNum) -> None:
        """
        使用矩形区域裁剪当前滤波区域
        """
        left = _handle_quantity(left, 'zonal_wavenumber').m
        right = _handle_quantity(right, 'zonal_wavenumber').m
        bottom = _handle_quantity(bottom, 'cpd').m
        top = _handle_quantity(top, 'cpd').m

        rectangle = Polygon([
            (left, bottom),
            (left, top),
            (right, top),
            (right, bottom)
        ])

        self.shape = self.shape.intersection(rectangle)

    def union(self, other: 'FilterArea') -> 'FilterArea':
        """返回当前滤波区域与另一个滤波区域的并集"""
        new_shape = self.shape.union(other.shape)
        new_attrs = FilterAreaAttributes(
            name=f"Union area",
            union_from=[self.attributes, other.attributes]
        )
        return FilterArea(new_shape, new_attrs)

    def intersection(self, other: 'FilterArea') -> 'FilterArea':
        """返回当前滤波区域与另一个滤波区域的交集"""
        new_shape = self.shape.intersection(other.shape)
        new_attrs = FilterAreaAttributes(
            name=f"Intersection area",
            intersection_from=[self.attributes, other.attributes]
        )
        return FilterArea(new_shape, new_attrs)

    def difference(self, other: 'FilterArea') -> 'FilterArea':
        """返回当前滤波区域与另一个滤波区域的差集，即当前区域减去另一个区域后的部分"""
        new_shape = self.shape.difference(other.shape)
        new_attrs = FilterAreaAttributes(
            name=f"Difference area",
            different={"origin_area": self.attributes,
                       "removed_area": other.attributes}
        )
        return FilterArea(new_shape, new_attrs)


class RectangleFilterArea(FilterArea):
    """矩形的FFT滤波区域"""
    def __init__(self,
                 min_wavenumber: QuantityOrNum, max_wavenumber: QuantityOrNum,
                 min_frequency: QuantityOrNum, max_frequency: QuantityOrNum):
        """创建一个 FFT 纬向波数-频率频谱中的矩形滤波区域。

        Parameters
        ----------
        min_wavenumber, max_wavenumber : QuantityOrNum
            矩形在纬向波数方向的两个边界值，默认单位为 'zonal_wavenumber'。
        min_frequency, max_frequency : QuantityOrNum
            矩形在频率方向的两个边界值，默认单位为 'cpd'。
        """
        min_wavenumber = _handle_quantity(min_wavenumber, 'zonal_wavenumber')
        max_wavenumber = _handle_quantity(max_wavenumber, 'zonal_wavenumber')
        min_frequency = _handle_quantity(min_frequency, 'cpd')
        max_frequency = _handle_quantity(max_frequency, 'cpd')

        shape = Polygon(
            [(min_wavenumber.m, min_frequency.m),
             (min_wavenumber.m, max_frequency.m),
             (max_wavenumber.m, max_frequency.m),
             (max_wavenumber.m, min_frequency.m)]
        )
        attrs = FilterAreaAttributes(
            name="Rectangle Filter Area",
            description="",
            parameters={
                "min_wavenumber": min_wavenumber,
                "max_wavenumber": max_wavenumber,
                "min_frequency": min_frequency,
                "max_frequency": max_frequency
            }
        )

        super().__init__(shape, attrs)


class EllipseFilterArea(FilterArea):
    """椭圆的FFT滤波区域"""
    def __init__(self,
                 center_wavenumber: QuantityOrNum, center_frequency: QuantityOrNum,
                 wavenumber_radius: QuantityOrNum, freq_radius: QuantityOrNum):
        """创建一个 FFT 纬向波数-频率频谱中的椭圆滤波区域。

        Parameters
        ----------
        center_wavenumber : QuantityOrNum
            椭圆中心在纬向波数方向的坐标，默认单位为 'zonal_wavenumber'。
        center_frequency : QuantityOrNum
            椭圆中心在频率方向的坐标，默认单位为 'cpd'。
        wavenumber_radius : QuantityOrNum
            椭圆在波数方向的半径，默认单位为 'zonal_wavenumber'。
        freq_radius : QuantityOrNum
            椭圆在频率方向的半径，默认单位为 'cpd'。
        """
        center_wavenumber = _handle_quantity(center_wavenumber, 'zonal_wavenumber')
        center_frequency = _handle_quantity(center_frequency, 'cpd')
        semi_major_axis = _handle_quantity(wavenumber_radius, 'zonal_wavenumber')
        semi_minor_axis = _handle_quantity(freq_radius, 'cpd')

        t = np.linspace(0, 2 * np.pi, 100)
        x = center_wavenumber.m + semi_major_axis.m * np.cos(t)
        y = center_frequency.m + semi_minor_axis.m * np.sin(t)
        points = np.array([x, y]).T

        shape = Polygon(points)
        attrs = FilterAreaAttributes(
            name="Ellipse Filter Area",
            description="",
            parameters={
                "center_wavenumber": center_wavenumber,
                "center_frequency": center_frequency,
                "semi_major_axis": semi_major_axis,
                "semi_minor_axis": semi_minor_axis
            }
        )

        super().__init__(shape, attrs)


class KelvinFilterArea(FilterArea):
    def __init__(self, min_depth: QuantityOrNum=8, max_depth: QuantityOrNum=90,
                 min_freq: QuantityOrNum=1/30, max_freq: QuantityOrNum=0.4,
                 min_wavenumber: QuantityOrNum=1,
                 max_wavenumber: QuantityOrNum=14,
                 g: QuantityOrNum=EARTH_GRAVITY,
                 beta: QuantityOrNum=ROSSBY_PARAMETER_ON_EQUATOR):
        """创建一个 Kelvin 波的 FFT 滤波区域，
        用于过滤出符合 Kelvin 波频散关系的信号。

        Parameters
        ----------
        min_depth, max_depth : QuantityOrNum, optional
            相当深度范围, 默认分别为 8 m 和 90 m
        min_freq, max_freq : QuantityOrNum, optional
            频率范围, 默认为 1/30 cpd 和 0.4 cpd
        min_wavenumber, max_wavenumber : QuantityOrNum, optional
            纬向波数范围, 默认为 1 和 14
        g : QuantityOrNum, optional
            重力加速度, by default EARTH_GRAVITY
        beta : QuantityOrNum, optional
            赤道上的罗斯贝参数, by default ROSSBY_PARAMETER_ON_EQUATOR
        """

        min_depth = _handle_quantity(min_depth, 'm')
        max_depth = _handle_quantity(max_depth, 'm')
        min_freq = _handle_quantity(min_freq, 'cpd')
        max_freq = _handle_quantity(max_freq, 'cpd')
        min_wavenumber = _handle_quantity(min_wavenumber, 'zonal_wavenumber')
        max_wavenumber = _handle_quantity(max_wavenumber, 'zonal_wavenumber')

        shape = Polygon([(0, 0),
            (50, self.to_cpd(np.sqrt(g * min_depth).m * 50)),
            (50, self.to_cpd(np.sqrt(g * max_depth).m * 50)),
        ])

        attrs = FilterAreaAttributes(
            name="Kelvin Wave Filter Area",
            description="",
            parameters={
                "min_depth": min_depth,
                "max_depth": max_depth,
                "min_frequency": min_freq,
                "max_frequency": max_freq,
                "min_wavenumber": min_wavenumber,
                "max_wavenumber": max_wavenumber,
                "g": g,
                "beta": beta
            }
        )

        super().__init__(shape, attrs)
        self._clip_by_rectangle(
            min_wavenumber, max_wavenumber,
            min_freq, max_freq
        )


class MRGFilterArea(FilterArea):
    def __init__(self,
                 min_depth: QuantityOrNum=8, max_depth: QuantityOrNum=90,
                 min_freq: QuantityOrNum=0.1, max_freq: QuantityOrNum=0.35,
                 min_wavenumber: QuantityOrNum=-10,
                 max_wavenumber: QuantityOrNum=-1,
                 g: QuantityOrNum=EARTH_GRAVITY,
                 beta: QuantityOrNum=ROSSBY_PARAMETER_ON_EQUATOR):
        """
        创建一个 Mixed Rossby-Gravity 波的 FFT 滤波区域，
        用于过滤出符合 MRG 波频散关系的信号。
        注意，此滤波区域包含西传 MRG 波和东传 MRG 波，只需要设置对应的波数范围即可。

            >>> # 西传 MRG 波滤波区域 （默认参数）
            >>> area = mew.MRGFilterArea(min_wavenumber=-10, max_wavenumber=-1)
            >>> # 东传 MRG 波滤波区域 （东传 MRG 波频率更大）
            >>> area = mew.MRGFilterArea(min_wavenumber=1, max_wavenumber=10,
                                        max_freq=0.85)
            >>> # 或者两者都包含
            >>> area = mew.MRGFilterArea(min_wavenumber=-10, max_wavenumber=10,
                                        max_freq=0.85)

        Parameters
        ----------
        min_depth, max_depth : QuantityOrNum, optional
            相当深度范围, 默认分别为 8 m 和 90 m
        min_freq, max_freq : QuantityOrNum, optional
            频率范围, 默认为 0.1 cpd 和 0.35 cpd
        min_wavenumber, max_wavenumber : QuantityOrNum, optional
            纬向波数范围, 默认为 -10 和 -1
        g : QuantityOrNum, optional
            重力加速度, by default EARTH_GRAVITY
        beta : QuantityOrNum, optional
            赤道上的罗斯贝参数, by default ROSSBY_PARAMETER_ON_EQUATOR
        """
        from ._dispersion import angular_frequency

        min_depth = _handle_quantity(min_depth, 'm')
        max_depth = _handle_quantity(max_depth, 'm')
        min_freq = _handle_quantity(min_freq, 'cpd')
        max_freq = _handle_quantity(max_freq, 'cpd')
        min_wavenumber = _handle_quantity(min_wavenumber, 'zonal_wavenumber')
        max_wavenumber = _handle_quantity(max_wavenumber, 'zonal_wavenumber')
        g = _handle_quantity(g, 'm/s**2')
        beta = _handle_quantity(beta, '1/(m*s)')

        k = np.linspace(max_wavenumber.m, min_wavenumber.m, 100) * \
            min_wavenumber.units
        omega1 = angular_frequency(EquatorialWave.MRGW, k,
                                   equivalent_depth=min_depth,
                                   g=g, beta=beta) / (2 * PI)
        omega2 = angular_frequency(EquatorialWave.MRGW, k,
                                   equivalent_depth=max_depth,
                                   g=g, beta=beta) / (2 * PI)
        line1 = np.array([k.m, omega1.m]).T
        line2 = np.array([k.m[::-1], omega2.m[::-1]]).T
        shape = Polygon(np.concatenate([line1, line2], axis=0))
        attrs = FilterAreaAttributes(
            name="MRG Wave Filter Area",
            parameters={
                "min_depth": min_depth,
                "max_depth": max_depth,
                "min_frequency": min_freq,
                "max_frequency": max_freq,
                "min_wavenumber": min_wavenumber,
                "max_wavenumber": max_wavenumber,
                "g": g,
                "beta": beta
            }
        )

        super().__init__(shape, attrs)
        self._clip_by_rectangle(
            min_wavenumber, max_wavenumber,
            min_freq, max_freq
        )


class ERFilterArea(FilterArea):
    def __init__(self, n: int = 1,
                 min_depth: QuantityOrNum=8, max_depth: QuantityOrNum=90,
                 min_freq: QuantityOrNum=1/60, max_freq: QuantityOrNum=1/5,
                 min_wavenumber: QuantityOrNum=-10,
                 max_wavenumber: QuantityOrNum=0,
                 g: QuantityOrNum=EARTH_GRAVITY,
                 beta: QuantityOrNum=ROSSBY_PARAMETER_ON_EQUATOR):
        """
        创建一个 Equatorial Rossby 波的 FFT 滤波区域，
        用于过滤出符合 ER 波频散关系的信号。
        因为 ER 波为西传波，所以波数需为负数。

        Parameters
        ----------
        n : int, optional
            埃尔米特多项式的阶数 n,需大于等于1，默认为 1。
        min_depth, max_depth : QuantityOrNum, optional
            相当深度范围, 默认分别为 8 m 和 90 m
        min_freq, max_freq : QuantityOrNum, optional
            频率范围, 默认为 1/60 cpd 和 1/5 cpd
        min_wavenumber, max_wavenumber : QuantityOrNum, optional
            纬向波数范围, 默认为 -10 和 0
        g : QuantityOrNum, optional
            重力加速度, by default EARTH_GRAVITY
        beta : QuantityOrNum, optional
            赤道上的罗斯贝参数, by default ROSSBY_PARAMETER_ON_EQUATOR
        """
        from ._dispersion import angular_frequency

        if n < 1:
            raise ValueError("n must be >= 1 for ER wave filter area.")
        if max_wavenumber > 0 or min_wavenumber > 0:
            raise ValueError("ER wave filter area only supports westward waves "
                             "(negative wavenumber).")

        min_depth = _handle_quantity(min_depth, 'm')
        max_depth = _handle_quantity(max_depth, 'm')
        min_freq = _handle_quantity(min_freq, 'cpd')
        max_freq = _handle_quantity(max_freq, 'cpd')
        min_wavenumber = _handle_quantity(min_wavenumber, 'zonal_wavenumber')
        max_wavenumber = _handle_quantity(max_wavenumber, 'zonal_wavenumber')
        g = _handle_quantity(g, 'm/s**2')
        beta = _handle_quantity(beta, '1/(m*s)')

        k = np.linspace(max_wavenumber.m, min_wavenumber.m, 100) * \
            min_wavenumber.units
        omega1 = angular_frequency(EquatorialWave.ERW, k,
                                   n=n, equivalent_depth=min_depth,
                                   g=g, beta=beta) / (2 * PI)
        omega2 = angular_frequency(EquatorialWave.ERW, k,
                                   n=n, equivalent_depth=max_depth,
                                   g=g, beta=beta) / (2 * PI)
        line1 = np.array([k.m, omega1.m]).T
        line2 = np.array([k.m[::-1], omega2.m[::-1]]).T
        shape = Polygon(np.concatenate([line1, line2], axis=0))
        attrs = FilterAreaAttributes(
            name=f"ER Wave (n={n}) Filter Area",
            parameters={
                "n": n,
                "min_depth": min_depth,
                "max_depth": max_depth,
                "min_frequency": min_freq,
                "max_frequency": max_freq,
                "min_wavenumber": min_wavenumber,
                "max_wavenumber": max_wavenumber,
                "g": g,
                "beta": beta
            }
        )

        super().__init__(shape, attrs)
        self._clip_by_rectangle(
            min_wavenumber, max_wavenumber,
            min_freq, max_freq
        )


class IGFilterArea(FilterArea):
    def __init__(self,
                 n: int = 1,
                 min_depth: QuantityOrNum=12, max_depth: QuantityOrNum=50,
                 min_freq: QuantityOrNum=0.3, max_freq: QuantityOrNum=0.7,
                 min_wavenumber: QuantityOrNum=-15,
                 max_wavenumber: QuantityOrNum=-1,
                 g: QuantityOrNum=EARTH_GRAVITY,
                 beta: QuantityOrNum=ROSSBY_PARAMETER_ON_EQUATOR):
        """
        创建一个 Inertio Gravity 波的 FFT 滤波区域，
        用于过滤出符合 IG 波频散关系的信号。
        注意，此滤波区域包含西传 IG 波和东传 IG 波，只需要设置对应的波数范围即可。

            >>> # 西传 IG 波滤波区域 （默认参数）
            >>> area = mew.IGFilterArea(min_wavenumber=-15, max_wavenumber=-1)
            >>> # 东传 IG 波滤波区域
            >>> area = mew.IGFilterArea(min_wavenumber=1, max_wavenumber=15)
            >>> # 或者两者都包含
            >>> area = mew.IGFilterArea(min_wavenumber=-15, max_wavenumber=15)

        Parameters
        ----------
        n : int, optional
            埃尔米特多项式的阶数 n,需大于等于1，默认为 1。
        min_depth, max_depth : QuantityOrNum, optional
            相当深度范围, 默认分别为 12 m 和 50 m
        min_freq, max_freq : QuantityOrNum, optional
            频率范围, 默认为 0.3 cpd 和 0.7 cpd
        min_wavenumber, max_wavenumber : QuantityOrNum, optional
            纬向波数范围, 默认为 -15 和 -1
        g : QuantityOrNum, optional
            重力加速度, by default EARTH_GRAVITY
        beta : QuantityOrNum, optional
            赤道上的罗斯贝参数, by default ROSSBY_PARAMETER_ON_EQUATOR
        """
        from ._dispersion import angular_frequency

        min_depth = _handle_quantity(min_depth, 'm')
        max_depth = _handle_quantity(max_depth, 'm')
        min_freq = _handle_quantity(min_freq, 'cpd')
        max_freq = _handle_quantity(max_freq, 'cpd')
        min_wavenumber = _handle_quantity(min_wavenumber, 'zonal_wavenumber')
        max_wavenumber = _handle_quantity(max_wavenumber, 'zonal_wavenumber')
        g = _handle_quantity(g, 'm/s**2')
        beta = _handle_quantity(beta, '1/(m*s)')

        if n < 1:
            raise ValueError("n must be >= 1 for IG wave filter area.")

        k = np.linspace(max_wavenumber.m, min_wavenumber.m, 100) * \
            min_wavenumber.units
        omega1 = angular_frequency(EquatorialWave.IGW, k, n=n,
                                   equivalent_depth=min_depth,
                                   g=g, beta=beta) / (2 * PI)
        omega2 = angular_frequency(EquatorialWave.IGW, k, n=n,
                                   equivalent_depth=max_depth,
                                   g=g, beta=beta) / (2 * PI)
        line1 = np.array([k.m, omega1.m]).T
        line2 = np.array([k.m[::-1], omega2.m[::-1]]).T
        shape = Polygon(np.concatenate([line1, line2], axis=0))
        attrs = FilterAreaAttributes(
            name=f"IG Wave (n={n}) Filter Area",
            parameters={
                "min_depth": min_depth,
                "max_depth": max_depth,
                "min_frequency": min_freq,
                "max_frequency": max_freq,
                "min_wavenumber": min_wavenumber,
                "max_wavenumber": max_wavenumber,
                "g": g,
                "beta": beta
            }
        )

        super().__init__(shape, attrs)
        self._clip_by_rectangle(
            min_wavenumber, max_wavenumber,
            min_freq, max_freq
        )


class MJOFilterArea(RectangleFilterArea):
    def __init__(self,
                 min_freq: QuantityOrNum=1/96, max_freq: QuantityOrNum=1/30,
                 min_wavenumber: QuantityOrNum=0.5,
                 max_wavenumber: QuantityOrNum=5,
                 ):
        """
        创建一个 MJO 的 FFT 滤波区域，用于过滤出符合 MJO 波频散关系的信号。
        此滤波区域为矩形区域。

        Parameters
        ----------
        min_freq, max_freq : QuantityOrNum, optional
            频率范围, 默认为 1/90 cpd (96日周期) 和 1/30 cpd (30日周期)
        min_wavenumber, max_wavenumber : QuantityOrNum, optional
            纬向波数范围, 默认为 0.5 和 5
        """
        super().__init__(
            min_wavenumber=min_wavenumber,
            max_wavenumber=max_wavenumber,
            min_frequency=min_freq,
            max_frequency=max_freq
        )


class TDFilterArea(RectangleFilterArea):
    def __init__(self,
                 min_freq: QuantityOrNum=1/6, max_freq: QuantityOrNum=1/2.5,
                 min_wavenumber: QuantityOrNum=-18,
                 max_wavenumber: QuantityOrNum=-8,
                 ):
        """
        创建一个 Tropical depression type 波的 FFT 滤波区域，
        用于过滤出符合 TD-type 波频散关系的信号。
        此滤波区域为矩形区域。

        Parameters
        ----------
        min_freq, max_freq : QuantityOrNum, optional
            频率范围, 默认为 1/6 cpd (6日周期) 和 1/2.5 cpd (2.5日周期)
        min_wavenumber, max_wavenumber : QuantityOrNum, optional
            纬向波数范围, 默认为 -18 和 -8
        """
        super().__init__(
            min_wavenumber=min_wavenumber,
            max_wavenumber=max_wavenumber,
            min_frequency=min_freq,
            max_frequency=max_freq
        )


