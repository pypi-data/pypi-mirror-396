#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
ComNetorchestrShowFun.py
========================

.. module:: Netterminal.Sources.Component.ComNetorchestrShowFun
  :platform: Windows, Linux
  :synopsis: NetOrchestr 可视化展示组件，整合地图渲染、时间进程管控、数据类型选择的核心功能。

.. moduleauthor:: WangXi

简介
----

该模块实现了**NetOrchestr 网络编排系统的可视化展示与数据类型管控**功能，主要用于**Netterminal 网络终端**应用程序中。
作为 ComBaseFun 的子类，它整合了 DevPltMap（地图可视化）、DevTimeProcess（时间进程）与 QComboBox（数据类型选择）组件，提供数据类型切换、地图初始化、时间进程管控等核心能力，是网络编排数据可视化的核心控制组件。

核心特性
--------

- 使用 PyQt5 组件（QComboBox）+ 自定义设备组件（DevPltMap/DevTimeProcess）呈现数据类型选择与可视化展示界面
- 支持基本的可视化控制操作（如数据类型切换、地图画布初始化、时间进程初始化、类型变更信号发射等）。
- 提供标准化的组件注册与初始化流程，适配 Netterminal 框架的组件管理规范

版本
----

- 版本 1.0 (2025/10/21): 初始版本，实现数据类型选择、地图/时间进程组件集成、类型变更信号通知核心逻辑
'''

from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from Netterminal.Sources.Component.ComBaseFun import ComBaseFun
from Netterminal.Sources.Device.DevPltMap import DevPltMap
from Netterminal.Sources.Device.DevTimeProcess import DevTimeProcess

class ComNetorchestrShowFun(ComBaseFun):
    """NetOrchestr 可视化展示控制组件
    
    整合数据类型选择、地图渲染、时间进程管控能力，
    是网络编排仿真结果可视化的核心交互组件。
    """
    
    data_type_changed_signal = pyqtSignal()
    """PyQt5 信号：数据类型变更信号
    
    当下拉选择框（datatype_choose_comboBox）的选中项变化时发射，
    通知数据层更新对应资源类型（cpu/ram/rom/band）的展示内容。
    """
    
    def __init__(self, name, **kwargs):
        super().__init__(name)
        self.name = name
        
        self.register(**kwargs)
        self.ready()
    
    def register(self, **kwargs):
        self.datatype_choose_comboBox:QComboBox = kwargs.get('datatype_choose_comboBox', None)
        self.devPltMap = DevPltMap("PltMap", **kwargs)
        self.devTimeProcess = DevTimeProcess("TimeProcess", **kwargs)
    
    def ready(self):
        self.datatype_choose_comboBox.addItems(["none", "cpu", "ram", "rom", "band"])
        self.datatype_choose_comboBox.setCurrentIndex(0)
        self.datatype_choose_comboBox.currentIndexChanged.connect(self.ctl_data_type_changed)
        self.devPltMap.ready()
        self.devTimeProcess.ready()

    @pyqtSlot()
    def ctl_data_type_changed(self):
        self.data_type_changed_signal.emit()

