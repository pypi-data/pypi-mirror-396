#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
"""
olink.py
=========

.. module:: netorchestr.envir.base.olink
  :platform: Windows
  :synopsis: 链路模块，基于 astropy 单位系统实现网络链路的时延建模与基础管理功能。

.. moduleauthor:: WangXi

简介
----

该模块实现了**网络链路时延建模与基础管控**的核心功能，主要用于**网络编排（NetOrchestr）** 应用程序中。
它基于 astropy.units 实现物理单位的标准化管理，确保链路时延的单位一致性与计算准确性，是网络仿真场景的基础组件。

核心特性
--------

- 使用 astropy.units 组件实现时延单位的标准化（支持 ms/s/us 等多单位自动转换）
- 支持链路名称自定义、时延动态配置等基础控制操作（如时延赋值、单位转换、属性查询等）。
- 与 OGate 门模块联动，为链路通信提供时延参数支撑

版本记录
--------

- 版本 1.0 (2025/07/11): 初始版本，实现链路对象的基础初始化、名称与时延属性管理
"""

from astropy import units as u

class OLink:
    """链路模型类（OLink），用于标准化管理网络链路的基础属性。

    该类基于 astropy.units 实现链路时延的物理单位管理，避免单位混乱问题，
    是 NetOrchestr 框架中网络拓扑仿真的核心基础类，可与 OGate、OModule 等模块联动。

    Attributes:
        name: 链路的唯一标识名称，用于拓扑中区分不同链路实例
        delay: 链路传输时延，带 astropy 物理单位（如 ms/s/us），支持单位自动转换
    """
    
    def __init__(self,name:str='Link',delay:u.Quantity=100*u.ms) -> None:
        """链路模型初始化

        Args:
            name (str, optional): 链路名称. 默认值为'Link'.
            delay (float, optional): 链路时延设置，单位ms. 默认值为100.0.
        """
        self.name = name
        self.delay:u.Quantity = delay
        