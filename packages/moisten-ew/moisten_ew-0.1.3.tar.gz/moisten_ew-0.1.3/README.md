# Moisten: Equatorial Waves

此模块为 Moisten 的一部分，包含了赤道波动相关的部分。
This module is part of Moisten and contains functionalities related to equatorial waves.

## 主要功能 / Features

 - 有量纲/无量纲的赤道波动频散关系计算（波数 k 计算角频率 ω）
 - 有量纲/无量纲赤道波动变量场（u, v, φ）的空间分布计算
 - 使用 FFT 对赤道波动进行频谱分析与滤波（WK99）
 - 一些滤波方法


## Build

To build the module, run:

```bash
uv build
```

To build the documentation, run:

```bash
mkdocs build
```