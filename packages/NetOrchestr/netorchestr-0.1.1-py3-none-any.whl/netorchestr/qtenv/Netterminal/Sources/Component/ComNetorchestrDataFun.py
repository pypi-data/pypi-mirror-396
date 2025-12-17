#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
ComNetorchestrDataFun.py
========================

.. module:: Netterminal.Sources.Component.ComNetorchestrDataFun
  :platform: Windows, Linux
  :synopsis: NetOrchestr 仿真数据处理组件，实现仿真结果加载、资源负载计算、节点运动数据解析与颜色映射核心功能。

.. moduleauthor:: WangXi

简介
----

该模块实现了**NetOrchestr 网络编排仿真数据的全流程解析与管理**功能，主要用于**Netterminal 网络终端**应用程序中。
作为 ComBaseFun 的子类，它整合了 DevFileSelector（文件选择）、pandas/numpy（数据处理）、astropy（单位管理）等组件，提供仿真数据加载、节点资源负载（CPU/RAM/ROM/带宽）计算、运动模型解析、负载值到RGB颜色映射等核心能力，是可视化展示的底层数据支撑组件。

核心特性
--------

- 使用 pandas/numpy/astropy 组件呈现仿真数据的结构化解析与单位标准化管理
- 支持基本的仿真数据控制操作（如文件路径校验、数据加载进度监控、资源负载计算、节点运动模型查询、负载值到RGB颜色映射等）。
- 提供标准化的信号通知机制（数据就绪信号），适配 PyQt5 界面的异步数据交互逻辑

版本
----

- 版本 1.0 (2025/10/21): 初始版本，实现仿真数据加载、资源负载计算、颜色映射、节点运动模型解析核心逻辑
'''

import numpy as np
import pandas as pd
import os
import logging
import pickle
import tqdm

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from astropy import units as u

from netorchestr.envir.mobility.base import MobilityBase 
from Netterminal.Sources.Component.ComBaseFun import ComBaseFun
from Netterminal.Sources.Device.DevFileSelector import DevFileSelector

class ComNetorchestrDataFun(ComBaseFun):
    """NetOrchestr 仿真数据处理核心组件
    
    负责仿真数据加载、资源负载计算、节点运动模型解析与负载颜色映射，
    为可视化展示提供底层数据支撑。
    """
    data_ready_signal = pyqtSignal()
    """PyQt5 信号：数据就绪信号
    
    当仿真数据（资源负载、节点运动轨迹）加载完成后发射，通知界面层数据可用于展示。
    """
    
    def __init__(self, name, **kwargs):
        super(ComNetorchestrDataFun,self).__init__(name)
        
        self.register(**kwargs)
        self.ready()
        
        self.data_ready_to_play = False
        
        
    def register(self, **kwargs):
        self.devFileSelector = DevFileSelector("FileSelector",**kwargs)

    def ready(self):
        self.devFileSelector.ready()
        self.devFileSelector.file_choosed_signal.connect(self.ctl_get_simulation_data)
        
    def ctl_get_simulation_data(self):
        self.data_ready_to_play = False
        if not os.path.exists(self.devFileSelector.file_path):
            logging.error(f"{self.__class__.__name__}:file {self.devFileSelector.file_path} not exist")
            return
        
        # 定位仿真结果文件位置
        self.data_resourse_file_path = self.devFileSelector.file_path
        self.data_resourse_dir_name = os.path.basename(os.path.dirname(self.data_resourse_file_path))
        self.data_node_mobility_file_name = self.data_resourse_dir_name.split('_')[0] + '_mobility.pkl'
        self.data_node_mobility_file_path = os.path.join(os.path.dirname(self.data_resourse_file_path),self.data_node_mobility_file_name)
        
        # 从仿真结果文件中提取信息
        self.data_resource_df = pd.read_csv(self.data_resourse_file_path)
        self.data_resource_timeseries = self.data_resource_df['Time'].values * u.ms
        self.data_node_mobility_list:list[MobilityBase] = []
        with open(self.data_node_mobility_file_path, 'rb') as f:
            self.data_node_mobility_list = pickle.load(f)
        self.data_resource_loads = {}
        
        # 添加数据加载进度条
        loads_progress = tqdm.tqdm(total=len(self.data_resource_timeseries),
                                   desc="INFO: 加载仿真数据中")
        
        for time in self.data_resource_timeseries:
            self.data_resource_loads[time] = self.ctl_get_data_resourse_value(time)
            loads_progress.update(1)
        loads_progress.close()
        
        logging.info(f"{self.__class__.__name__}: simulation data loaded")
        
        self.data_ready_signal.emit()
        
        
    def ctl_get_data_resourse_value(self,time):
        if time not in self.data_resource_timeseries:
            logging.error(f"time {time} not exist in simulation data")
            return
        
        cpu_usage_rate_dict = {}
        ram_usage_rate_dict = {}
        rom_usage_rate_dict = {}
        band_usage_rate_dict = {}
        
        for node_mobility in self.data_node_mobility_list:
            node_name = node_mobility.name.split('_')[0]
            
            cpu_key = f'{node_name}_cpu'
            ram_key = f'{node_name}_ram'
            rom_key = f'{node_name}_rom'
            band_key = f'{node_name}_band'
            
            required_keys = {cpu_key, ram_key, rom_key, band_key}
            if not required_keys.issubset(self.data_resource_df.keys()):
                logging.warning(f"{self.__class__.__name__}: node {node_name} cpu/ram/rom key not exist in simulation data")
                continue
            
            total_cpu = self.data_resource_df[cpu_key].iloc[0]
            total_ram = float(self.data_resource_df[ram_key].iloc[0].split(' ')[0])
            total_rom = float(self.data_resource_df[rom_key].iloc[0].split(' ')[0])
            total_band = float(self.data_resource_df[band_key].iloc[0].split(' ')[0])
            
            index = np.where(self.data_resource_timeseries == time)[0][0]
            
            cpu_usage_rate = (total_cpu - self.data_resource_df[cpu_key].iloc[index]) / total_cpu
            ram_usage_rate = (total_ram - float(self.data_resource_df[ram_key].iloc[index].split(' ')[0])) / total_ram
            rom_usage_rate = (total_rom - float(self.data_resource_df[rom_key].iloc[index].split(' ')[0])) / total_rom
            band_usage_rate = (total_band - float(self.data_resource_df[band_key].iloc[index].split(' ')[0])) / total_band
            
            cpu_usage_rate_dict[node_name] = cpu_usage_rate
            ram_usage_rate_dict[node_name] = ram_usage_rate
            rom_usage_rate_dict[node_name] = rom_usage_rate
            band_usage_rate_dict[node_name] = band_usage_rate
        
        
        resouce_dict = {"cpu":cpu_usage_rate_dict, 
                        "ram":ram_usage_rate_dict, 
                        "rom":rom_usage_rate_dict, 
                        "band":band_usage_rate_dict}
        return resouce_dict


    def ctl_get_nodes_load_colors(self, time, resourse_type:str):
        """得到节点集合的资源负载所对应的颜色集合

        Args:
        
            time (float): 仿真进行时间
            
            resourse_type (str): 资源类型, 如None、cpu、ram、rom、band

        Returns:
            
            如果 resourse_type 为 None, 则返回:
            
            dict[str,str]: 一个包含节点名为键, 节点自身颜色为值的字典。
            
            如果 resourse_type 不为 None, 则返回:
            
            dict[str,np.ndarray]: 一个包含节点名为键, 形状为(3,)的数组为RGB颜色值(0-255)/255的字典。
        """
        if time not in self.data_resource_timeseries:
            logging.error(f"{self.__class__.__name__}: time {time} not exist in simulation data")
            return
        
        if resourse_type == "none":
            rgb_colors_dict = {}
            for mobility_model in self.data_node_mobility_list:
                rgb_colors_dict[mobility_model.name.split('_')[0]] = mobility_model.markcolor
            return rgb_colors_dict
        
        try:
            nodes_load = self.data_resource_loads[time][resourse_type]
            return self._rates_to_rgb(nodes_load)
        except KeyError:
            logging.error(f"{self.__class__.__name__}: resourse_type {resourse_type} not exist in simulation data")
        
        
        
    def _rates_to_rgb(self, load_values_dict:dict[str,float]) -> dict[str,list[float]]:
        """
        将资源负载值(0-1范围的小数)映射为RGB颜色值。
        
        参数:
            load_values (dict[str,float]): 一个包含节点名和0到1之间小数的字典,表示资源负载。
            
        返回:
            dict[str,np.ndarray]: 一个包含节点名和形状为 (3,) 的数组,每一行是一个RGB颜色值(范围在0-255之间)。
        """
        load_values = np.array(list(load_values_dict.values()))
        if not np.all((load_values >= 0) & (load_values <= 1)):
            raise ValueError("ctl_load_to_rgb函数的所有输入负载值必须在0到1之间")
        
        # 定义颜色映射：从蓝色（低负载）到红色（高负载），使用非线性过渡
        def interpolate_color(value):
            # 非线性调整：让红色更容易出现
            adjusted_value = value ** 0.5  # 平方根函数加速红色的出现
            
            if adjusted_value < 0.25:
                # 从深蓝色到浅蓝色过渡
                r = int(64 * (adjusted_value / 0.25))  # 增加一点柔和的红
                g = int(64 * (adjusted_value / 0.25))  # 增加一点柔和的绿
                b = 128 + int(127 * (adjusted_value / 0.25))  # 蓝色为主
            elif adjusted_value < 0.5:
                # 从浅蓝色到浅绿色过渡
                r = int(64 * (1 - (adjusted_value - 0.25) / 0.25))
                g = 128 + int(127 * ((adjusted_value - 0.25) / 0.25))
                b = 255 - int(127 * ((adjusted_value - 0.25) / 0.25))
            elif adjusted_value < 0.75:
                # 从浅绿色到橙色过渡
                r = 128 + int(127 * ((adjusted_value - 0.5) / 0.25))
                g = 255 - int(127 * ((adjusted_value - 0.5) / 0.25))
                b = 0
            else:
                # 从橙色到柔和的红色过渡
                r = 255
                g = int(64 * (1 - (adjusted_value - 0.75) / 0.25))  # 减少绿色，保持柔和
                b = 0
            
            return [r/255, g/255, b/255]
        
        # 对每个负载值计算对应的 RGB 值
        rgb_colors = np.array([interpolate_color(value) for value in load_values])
        
        # 转换为字典格式
        rgb_colors_dict = {node_name: color for node_name, color in zip(load_values_dict.keys(), rgb_colors)}
        
        return rgb_colors_dict
    
    
    def ctl_get_mobility_model(self, node_name:str):
        for mobility_model in self.data_node_mobility_list:
            if mobility_model.name.split("_")[0] == node_name:
                return mobility_model
            