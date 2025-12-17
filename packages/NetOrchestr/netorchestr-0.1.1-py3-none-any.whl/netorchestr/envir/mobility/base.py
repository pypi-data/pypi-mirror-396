#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
'''
mobility.py
===========

.. module:: netorchestr.envir.mobility
  :platform: Windows
  :synopsis: 节点运动模型核心模块，实现地理坐标管理、坐标转换、距离计算、静态/动态运动模型定义等能力。

.. moduleauthor:: WangXi

简介
----

该模块实现了**网络仿真中节点运动模型的标准化管理**功能，主要用于**NetOrchestr 网络编排**应用程序中。
作为节点运动轨迹管控的基础模块，它提供了地理坐标（GPS）与笛卡尔坐标的精确转换、两点距离计算、矩形区域随机坐标生成、静态/动态运动模型基类定义等核心能力，支撑仿真中节点位置的动态更新与可视化。

核心特性
--------

- 使用 astropy 天文时间/单位系统，实现高精度的时间与坐标单位管控
- 支持基本的运动模型控制操作（如GPS坐标初始化/更新、地理坐标转笛卡尔坐标、两点距离计算、矩形区域随机坐标生成等）。
- 定义静态（MobilityStatic）/动态（MobilityDynamic）运动模型基类，支持子类扩展自定义运动轨迹

版本
----

- 版本 1.0 (2025/07/11): 初始版本，实现运动模型基类、坐标转换、距离计算、随机坐标生成核心逻辑
'''

import math
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation
from typing import Union

class MobilityBase():
    def __init__(self, name:str, init_time:Time, init_gps:list[float], markcolor:str='black'):
        """运动模型基类初始化
        
        Args:
            name (str): 运动模型名称
            init_time (Time): 运动模型初始化时间
            init_gps (list[float]): 运动模型初始化的地理坐标 [经度, 纬度, 高度km]
            markcolor (str, optional): 运动模型的标记颜色. Defaults to 'black'.
        """
        self.name = name
        self.markcolor = markcolor
        
        self.init_time:Time = init_time
        self.current_time: Time = init_time
        
        self.init_gps = init_gps
        """地理坐标系下初始坐标 [经度, 纬度, 高度km]"""
        
        self.current_gps = init_gps
        """地理坐标系下当前坐标 [经度, 纬度, 高度km]"""
        
        self.cache_gps:dict[Time, list[float]] = {}
        """缓存的历史坐标 {时间: [经度, 纬度, 高度km]}"""
        

    def set_init_gps(self, gps:list[float]):
        """设置初始的地理坐标"""
        self.init_gps = gps
        self.current_gps = gps
        
        
    def update_current_gps(self, time:u.Quantity):
        """更新当前的地理坐标 (该方法需要子类继承实现)
        
        Args:
            time (u.Quantity): 仿真开始后经历的时间
        
        Returns:
            list[float]: [经度, 纬度, 高度]
            
            bool: 是否是从缓存中获取的坐标
        """
        self.current_time = self.init_time + np.around(time.to(u.ms))
        # 检查缓存中是否有当前时间的坐标
        if self.current_time in self.cache_gps:
            self.current_gps = self.cache_gps[self.current_time]
            return self.current_gps, True

        # 子类需要实现更新坐标的逻辑
        # 缓存当前时间坐标
        self.cache_gps[self.current_time] = self.current_gps
        return self.current_gps, False

    def get_gps2xyz(self) -> list[float]:
        """实现从地理坐标到笛卡尔坐标的精确转换。

        Returns:
            list[float]: [X, Y, Z] 单位为千米 (km)
        """
        lon = self.current_gps[0]  # 经度 (°)
        lat = self.current_gps[1]  # 纬度 (°)
        alt_km = self.current_gps[2]  # 高度 (km)

        alt = alt_km * 1000  # 将高度从千米转换为米

        # WGS84椭球参数
        a = 6378137.0  # 长半轴，单位：米
        b = 6356752.314245  # 短半轴，单位：米
        f = (a - b) / a  # 扁率
        e_squared = 1 - (b**2 / a**2)  # 第一偏心率平方
        
        lat_rad = math.radians(lat)  # 纬度转弧度
        lon_rad = math.radians(lon)  # 经度转弧度
        
        # 计算卯酉圈曲率半径 N
        N = a / math.sqrt(1 - e_squared * math.sin(lat_rad)**2)
        
        # 计算笛卡尔坐标 X, Y, Z (单位：米)
        X_m = (N + alt) * math.cos(lat_rad) * math.cos(lon_rad)
        Y_m = (N + alt) * math.cos(lat_rad) * math.sin(lon_rad)
        Z_m = ((b**2 / a**2) * N + alt) * math.sin(lat_rad)
        
        # 将结果从米转换为千米
        X_km = X_m / 1000
        Y_km = Y_m / 1000
        Z_km = Z_m / 1000
        
        return [X_km, Y_km, Z_km]

    @staticmethod
    def calculate_distance(gps1: list, gps2: list) -> u.quantity:
        """使用 Astropy 包计算两个GPS坐标之间的直线距离

        计算依据
        1. 使用 EarthLocation 将经纬度转换为三维空间中的位置
        2. 使用 SkyCoord 的 separation_3d 方法计算两点间的三维距离
        3. 返回的距离单位为千米, km

        Args:
            gps1 (list): 第一个GPS坐标 [经度, 纬度, 高度km]
            gps2 (list): 第二个GPS坐标 [经度, 纬度, 高度km]

        Returns:
            u.quantity: 两点之间的直线距离
        """
        lon1, lat1, alt1 = gps1
        lon2, lat2, alt2 = gps2

        # 创建 EarthLocation 对象
        loc1 = EarthLocation.from_geodetic(lon=lon1 * u.deg, lat=lat1 * u.deg, height=alt1 * u.km)
        loc2 = EarthLocation.from_geodetic(lon=lon2 * u.deg, lat=lat2 * u.deg, height=alt2 * u.km)

        distance = np.sqrt((loc1.x - loc2.x)**2 + (loc1.y - loc2.y)**2 + (loc1.z - loc2.z)**2)
        return distance

    @staticmethod
    def get_rectangular_area(gps_group: Union[list, dict]):
        """计算一组GPS坐标围成的矩形区域的四个顶点的坐标

        Args:
            gps_group (Union[list, dict]): 包含GPS坐标的列表或字典, 格式为 [经度, 纬度, 高度km] 或 {地名: [经度, 纬度, 高度km]}

        Returns:
            dict: 矩形区域的四个顶点的坐标 
            {
                "left_bottom": [经度, 纬度, 0], 
                "left_top": [经度, 纬度, 0], 
                "right_top": [经度, 纬度, 0], 
                "right_bottom": [经度, 纬度, 0]}
        """
        if isinstance(gps_group, list):
            gps_list = gps_group
        elif isinstance(gps_group, dict):
            gps_list = list(gps_group.values())
        else:
            raise TypeError("gps_group should be a list or a dictionary")

        left_bottom = [min(gps_list, key=lambda x: x[0])[0], min(gps_list, key=lambda x: x[1])[1], 0]
        left_top = [min(gps_list, key=lambda x: x[0])[0], max(gps_list, key=lambda x: x[1])[1], 0]
        right_top = [max(gps_list, key=lambda x: x[0])[0], max(gps_list, key=lambda x: x[1])[1], 0]
        right_bottom = [max(gps_list, key=lambda x: x[0])[0], min(gps_list, key=lambda x: x[1])[1], 0]

        area = {
            "left_bottom": left_bottom,
            "left_top": left_top,
            "right_top": right_top,
            "right_bottom": right_bottom
        }
        return area
    
    @staticmethod
    def get_random_gpslist_in_rectangular_area(area: dict, num: int, seed: int=None) -> list:
        """在矩形区域内随机生成指定数量的GPS坐标

        Args:
            area (dict): 矩形区域的四个顶点的坐标
            {
                "left_bottom": [经度, 纬度, 0], 
                "left_top": [经度, 纬度, 0], 
                "right_top": [经度, 纬度, 0], 
                "right_bottom": [经度, 纬度, 0]}
            num (int): 要生成的GPS坐标数量
            seed (int, optional): 随机数种子. Defaults to None.

        Returns:
            list: 包含随机生成的GPS坐标的列表
        """
        if seed is not None:
            np.random.seed(seed)
        
        left_bottom = area["left_bottom"]
        right_top = area["right_top"]

        x_min, y_min = left_bottom[0], left_bottom[1]
        x_max, y_max = right_top[0], right_top[1]

        x_list = np.random.uniform(x_min, x_max, num)
        y_list = np.random.uniform(y_min, y_max, num)
        z_list = np.zeros(num)

        gps_list = [[x, y, z] for x, y, z in zip(x_list, y_list, z_list)]
        return gps_list

class MobilityStatic(MobilityBase):
    def __init__(self, name:str, init_time:Time, init_gps:list[float], markcolor:str='black'):
        super().__init__(name, init_time, init_gps, markcolor)
        
    
class MobilityDynamic(MobilityBase):
    def __init__(self, name:str, init_time:Time, init_gps:list[float], markcolor:str='green'):
        super().__init__(name, init_time, init_gps, markcolor)
        