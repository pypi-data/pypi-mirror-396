#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
'''
onet.py
=========

.. module:: netorchestr.envir.onet
  :platform: Windows
  :synopsis: 网络仿真核心模块，实现离散事件驱动的网络拓扑仿真、节点运动可视化、仿真过程管控等全流程能力。

.. moduleauthor:: WangXi

简介
----

该模块实现了**离散事件驱动的网络系统全生命周期仿真**功能，主要用于**NetOrchestr 网络编排**应用程序中。
作为仿真框架的顶层入口，它整合了模块管理、时间调度、无线介质适配、节点运动可视化、仿真进度监控等核心能力，支持大规模网络节点的并行仿真与结果分析。

核心特性
--------

- 使用 simpy 离散事件仿真环境 + astropy 时间系统，实现高精度（毫秒级）的仿真时间管控
- 支持基本的网络仿真全流程控制操作（如模块注册、无线介质关联、仿真运行/监控、节点运动轨迹可视化、仿真结果持久化等）。
- 集成 cartopy/matplotlib 实现地理空间可视化，支持仿真过程的 GIF 动画生成；基于 joblib 实现并行化绘图提升效率

版本
----

- 版本 1.0 (2025/07/11): 初始版本，实现仿真环境初始化、模块管理、仿真运行、节点运动可视化核心逻辑
'''

import os
import simpy
import tqdm
import numpy as np
from astropy.time import Time
from astropy import units as u
from joblib import Parallel, delayed
import pickle

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import imageio.v2 as imageio

from netorchestr.eventlog import OLogger
from netorchestr.envir.base import OModule
from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.physicallayer import RadioMedium, RadioPhy
from netorchestr.common.util import DataAnalysis

class ONet:
    def __init__(self, 
                 name:str, 
                 sim_id:str = "", 
                 seed_id:int = 0,
                 work_dir:str = None):
        
        self.name = name
        self.scheduler = simpy.Environment()
        self.logger = OLogger(name=name+"_logger",
                              sim_id=sim_id,
                              seed_id=seed_id,
                              work_dir=work_dir)
        
        # self.logger.debug_file_handler.setLevel("ERROR")
        
        self.modules:list["OModule"] = []
        """模块列表"""
        
        self.astro_time_init:Time = None
        """开始仿真的天文时间"""
        
        self.sim_time_accuracy:Time = 1 * u.ms
        """仿真时间精度, 单位为ms, 默认为1ms"""
           
        self.sim_time_until:Time = 1 * u.s
        """仿真结束时间, 单位为ms, 默认为1s"""
        
    def add_module(self, module:"OModule"):
        self.modules.append(module)
    
    
    def find_modules_with_class(self, module_class)->list["OModule"]:
        """查找指定类型的模块
        
        Args:
            module_class (class ot tuple): 指定的模块类型
        
        """
        modules = []
        def traverse_module(module:"OModule"):
            if isinstance(module, module_class):
                modules.append(module)
            
            for submodule in module.oSubModules:
                traverse_module(submodule)
        
        for module in self.modules:
            traverse_module(module)
        
        return modules
        
    
    def ready_for_medium(self, radio_medium:"RadioMedium"):
        """准备传输介质模块"""
        self.radio_medium = radio_medium
        
        for module in self.find_modules_with_class(RadioPhy):
            NodeBase.connect_layer_submodules([module, radio_medium])
            self.logger.debug(f"{self.scheduler.now}: {module.name} connected to {radio_medium.name}")

    
    def update_process(self):
        """仿真进度条更新进程"""
        if not hasattr(self, 'process_bar'):
            total_step = int(self.sim_time_until.to(u.ms).value / self.sim_time_accuracy.to(u.ms).value)
            self.process_bar = tqdm.tqdm(total=total_step, desc=f"INFO: 运行仿真中")
        
        while True:
            if hasattr(self, 'process_bar'):
                self.process_bar.desc = f"INFO: 运行仿真天文时{DataAnalysis.format_milliseconds(self.scheduler.now)}"
                self.process_bar.update(1)
                
            yield self.scheduler.timeout(self.sim_time_accuracy.to(u.ms).value)
    
    
    def get_all_mobility_models(self)->list:
        """获取参与仿真的所有节点的运动模型"""
        mobility_models = []
        for module in [temp_module for temp_module in self.modules if hasattr(temp_module, 'mobiusTraj')]:
            mobility = module.mobiusTraj
            mobility_models.append(mobility)
        return mobility_models
    
    
    def save_all_mobility_models(self):
        mobility_models = self.get_all_mobility_models()
        with open(os.path.join(self.logger.log_dir, f"{self.name}_mobility.pkl"), "wb") as f:
            pickle.dump(mobility_models, f)
    

    def draw_joblib(self, time_start:u.quantity, time_until:u.quantity, 
                    time_accuracy:u.quantity, draw_region:list[float], frames_path:str = None):
        """以joblib并行化的方式绘制地图"""
        time_list = np.arange(time_start.to(u.ms).value, 
                              time_until.to(u.ms).value+1.0, 
                              time_accuracy.to(u.ms).value) * u.ms
        
        step_list = range(int(time_until.to(u.s).value / time_accuracy.to(u.s).value) + 1)
        
        mobility_models = self.get_all_mobility_models()
            
        def draw_frame(time, currunt_step, total_step, mobility_models, draw_region):
            import warnings
            warnings.filterwarnings("ignore", message="facecolor will have no effect as it has been defined as \"never\".")
            
            # 初始化图形和轴
            fig = plt.figure(figsize=(6, 4))
            ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            ax.set_extent(draw_region, crs=ccrs.PlateCarree())
            
            # 添加地图特征
            ax.add_feature(cfeature.LAND, facecolor='grey', edgecolor='none', alpha=0.7)
            ax.add_feature(cfeature.OCEAN, facecolor='#A6CAE0', edgecolor='none')
            ax.add_feature(cfeature.COASTLINE, linewidth=0.1, color='white')
            
            # 绘制网格线
            gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                            linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            gl.xformatter = LONGITUDE_FORMATTER
            gl.yformatter = LATITUDE_FORMATTER
            
            for mobility_model in mobility_models:
                mobility_model.update_current_gps(time)
                ax.scatter(mobility_model.current_gps[0], mobility_model.current_gps[1], 
                        s=20, alpha=0.7, c=mobility_model.markcolor, edgecolors="black", 
                        label=mobility_model.name, transform=ccrs.PlateCarree())
                ax.text(mobility_model.current_gps[0], mobility_model.current_gps[1], 
                        mobility_model.name.split("_")[0], transform=ccrs.PlateCarree(), ha="center", va="center", fontsize=6)
            
            from netorchestr.envir.mobility import MobilityBase
            
            for mobility_model in mobility_models[0:40]:
                for other_mobility_model in mobility_models[40:]:
                    if mobility_model is not other_mobility_model:
                        try:
                            if MobilityBase.calculate_distance(mobility_model.current_gps, other_mobility_model.current_gps) < 1000 * u.km:
                                ax.plot([mobility_model.current_gps[0], other_mobility_model.current_gps[0]],
                                        [mobility_model.current_gps[1], other_mobility_model.current_gps[1]],
                                        color="black", linewidth=0.1, transform=ccrs.Geodetic()
                                        )
                        except:
                            continue
            
            # plt.tight_layout()
            plt.title(f"{DataAnalysis.format_milliseconds(time.to(u.ms).value,languange='en')}", loc="left")

            # 保存帧（按序号命名确保顺序）
            frame_path = os.path.join(frames_path,f"frame_{currunt_step:0{len(str(total_step))}d}.png")
            plt.savefig(frame_path, dpi=150)
            plt.close()
            
        Parallel(n_jobs=-1, verbose=10)(
            delayed(draw_frame)(time, currunt_step, len(step_list), mobility_models, draw_region) 
            for time, currunt_step in zip(time_list, step_list))
            
    def get_area_gif(self, time_start:u.quantity, time_until:u.quantity, 
                     time_accuracy:u.quantity, draw_region:list[float], 
                     filename:str = None):
        """获取区域动画
        
        可不运行仿真, 直接获取区域动画
        
        """
        print("INFO: 制作动画帧中")
        frames_path = os.path.join(self.logger.log_dir, "frames")
        os.makedirs(frames_path, exist_ok=True)
        self.draw_joblib(time_start, time_until, time_accuracy, draw_region, frames_path)
        print("INFO: 合并帧为动画")
        frames = []
        for file_name in sorted(os.listdir(frames_path)):
            frames.append(imageio.imread(os.path.join(frames_path, file_name)))
            
        if filename is None:
            imageio.mimsave(os.path.join(self.logger.log_dir, f"{self.name}.gif"), frames, fps = 10, loop = 0)
        else:
            imageio.mimsave(os.path.join(self.logger.log_dir, f"{filename}.gif"), frames, fps = 10, loop = 0)
        
        # 删除帧文件
        import shutil
        shutil.rmtree(frames_path)
    
    def run(self,until:u.quantity):
        """运行仿真, 直到仿真时间到达until

        Args:
            until (u.quantity): 仿真终止时间
        """
        start_time = Time.now()
        
        self.sim_time_until = until
        print(f"INFO: 仿真天文时长 {DataAnalysis.format_milliseconds(until.to(u.ms).value)}")
        
        print("INFO: 激活所有模块")
        for module in self.modules:
            module._activate(self.scheduler, self.logger)

        self.scheduler.process(self.update_process())
        self.scheduler.run(until=self.sim_time_until.to(u.ms).value)
        
        if hasattr(self, 'process_bar'):
            self.process_bar.close()
            delattr(self, 'process_bar')  # 清理引用，允许重新创建
        
        print("INFO: 仿真结束")
        
        end_time = Time.now()
        print(f"INFO: 仿真总耗时 {DataAnalysis.format_milliseconds((end_time - start_time).to(u.ms).value)}")
        
        print("INFO: 节点移动模型保存")
        self.save_all_mobility_models()
        

