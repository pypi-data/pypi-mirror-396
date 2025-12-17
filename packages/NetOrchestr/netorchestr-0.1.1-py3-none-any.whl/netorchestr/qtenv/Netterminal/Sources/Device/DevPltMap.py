#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
DevPltMap.py
============

.. module:: Netterminal.Sources.Device.DevPltMap
  :platform: Windows, Linux
  :synopsis: PyQt5 地图可视化模块，基于 Matplotlib + Cartopy 实现交互式地理空间绘图与动态元素管控。

.. moduleauthor:: WangXi

简介
----

该模块实现了**PyQt5 界面下的交互式地理空间可视化**功能，主要用于**Netterminal 网络终端**应用程序中。
作为 DevPltBoard 的子类，它整合了 Matplotlib 与 Cartopy 库，提供地图基础渲染、动态元素（点/文本）添加/更新/清除、软刷新等核心能力，支撑地理坐标相关的可视化需求。

核心特性
--------

- 使用 Matplotlib + Cartopy 组件呈现全球/自定义区域的地理地图（含陆地、海洋、海岸线等基础特征）
- 支持基本的地图交互控制操作（如动态添加/更新散点/文本、清除叠加元素、画布软刷新、地图区域范围自定义等）。
- 适配 PyQt5 界面框架，提供工具栏集成、布局管理、画布高效刷新等 Qt 交互能力

版本
----

- 版本 1.0 (2025/10/21): 初始版本，实现地图基础渲染、动态元素管控、PyQt5 界面集成核心逻辑
'''

import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from Netterminal.Sources.Device.DevBase import DevBase
from Netterminal.Sources.Device.DevPltBoard import DevPltBoard

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.colors import ListedColormap
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import warnings
warnings.filterwarnings("ignore", message="facecolor will have no effect as it has been defined as \"never\".")

class DevPltMap(DevPltBoard):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        
        self.region:list[float] = [-180,180,-90,90]  # 地图区域范围
        
        self.dynamic_artists = {}  # 仅记录动态添加的元素（id: 点、线、文本等）
        
    def ready(self):
        """初始化画板，创建 Matplotlib 画布和工具栏"""
        # 清除外部控件的现有布局（如果有的话）
        layout = self.pltboard_widget.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            layout = QVBoxLayout()
            self.pltboard_widget.setLayout(layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self.pltboard_widget)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # 初始化图形和轴
        self.ax = self.figure.add_subplot(1,1,1,projection=ccrs.PlateCarree())
        self.ax.set_extent(self.region, crs=ccrs.PlateCarree())
        
        # 添加地图特征
        self.ax.add_feature(cfeature.LAND, facecolor='grey', edgecolor='none', alpha=0.7)
        self.ax.add_feature(cfeature.OCEAN, facecolor='#A6CAE0', edgecolor='none')
        self.ax.add_feature(cfeature.COASTLINE, linewidth=0.1, color='white')
        
        # 绘制网格线
        gl = self.ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                               linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        
        # 设置坐标轴标签的字号和颜色
        gl.xlabel_style = {'size': 20, 'color': 'white'}
        gl.ylabel_style = {'size': 20, 'color': 'white'}
        
        self.ax.spines["top"].set_visible(False)    # 隐藏顶部边框
        self.ax.spines["right"].set_visible(False)  # 隐藏右侧边框
        self.ax.spines["left"].set_visible(False)   # 隐藏左侧边框
        self.ax.spines["bottom"].set_visible(False) # 隐藏底部边框

        self.canvas.draw()

    def ctl_preadd_scatter(self, scatter_id:str, lon: float, lat: float, **kwargs):
        """在地图上预备添加点, 添加后需刷新画板"""
        if scatter_id not in self.dynamic_artists.keys():
            scatter_obj = self.ax.scatter(lon, lat, transform=ccrs.PlateCarree(), **kwargs)
            self.dynamic_artists[scatter_id] = scatter_obj  # 记录动态元素
        else:
            scatter_obj = self.dynamic_artists[scatter_id]
            scatter_obj.set_offsets(np.array([[lon, lat]]))
            scatter_color = kwargs.get("color",None)
            if scatter_color is not None:
                scatter_obj.set_color(scatter_color)
    
    def ctl_preadd_text(self, text_id:str, lon: float, lat: float, text: str, **kwargs):
        """在地图上预备添加文本, 添加后需刷新画板"""
        if text_id not in self.dynamic_artists.keys():
            text_obj = self.ax.text(lon, lat, text, transform=ccrs.PlateCarree(), **kwargs)
            self.dynamic_artists[text_id] = text_obj  # 记录动态元素
        else:
            text_obj = self.dynamic_artists[text_id]
            text_obj.set_position((lon, lat))

    def ctl_clear_overlay(self):
        """清除画布上所有动态添加的点、线、文本等，保留地图基础元素"""
        # 遍历并删除所有动态添加的元素
        for artist in self.dynamic_artists.values():
            if artist in self.ax.get_children():  # 确保元素仍存在于轴中
                artist.remove()
        self.dynamic_artists.clear()  # 清空记录列表
        self.canvas.draw()  # 重新绘制
    
    def ctl_refresh_softly(self):
        # 仅更新变化区域
        self.canvas.draw_idle()

