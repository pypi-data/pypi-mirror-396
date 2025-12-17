#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
AppNetorchestr.py
=================

.. module:: AppNetorchestr
  :platform: Windows, Linux
  :synopsis: NetOrchestr仿真结果可视化模块, 用于展示仿真结果的可视化功能。

.. moduleauthor:: WangXi

简介
----

该模块实现了NetOrchestr仿真结果可视化模块的功能, 主要用于展示仿真结果。它提供了以下特性：

- 使用 PyQt5 库实现了仿真结果可视化的图形界面组件呈现

版本
----

- 版本 1.0 (2025/10/21): 初始版本

'''

import os
import logging
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction
from PyQt5.QtCore import pyqtSlot

from netorchestr.common.util import DataAnalysis
from Netterminal.Sources.App.AppNetorchestr import Ui_MainWindow_Netorchestr
from Netterminal.Sources.Component.ComNetorchestrShowFun import ComNetorchestrShowFun
from Netterminal.Sources.Component.ComNetorchestrDataFun import ComNetorchestrDataFun
from Netterminal.Sources.Component.ComNetorchestrCalFun import ComNetorchestrCalFun
from Netterminal.Sources.Component.ComNetorchestrEventFun import ComNetorchestrEventFun

class AppNetorchestr(QMainWindow, Ui_MainWindow_Netorchestr):
    def __init__(self, parent=None):
        super(AppNetorchestr, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('NetOrchestr GUI')
        
        sources_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        style_file_path = os.path.join(sources_dir,'Style', 'MaterialDark.qss')
        with open(style_file_path, 'r', encoding="utf-8") as f:
            qssStyle = f.read()
        self.setStyleSheet(qssStyle)
        
        screen = QDesktopWidget().screenGeometry()
        screenWidth = screen.width()
        screenHeight = screen.height()
        self.resize(int(screenWidth * 0.6), int(screenHeight * 0.9))
        
        logging.basicConfig(
            level=logging.ERROR,  # 设置全局日志级别
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        
        self.plt_background_color = [30/255, 29/255, 35/255]

        self.initComponent()
        
        self.ready()
        
        # 设置状态栏
        self.statusBar().showMessage('就绪')
    
    def open_new_window(self):
        self.comNetorchestrCalFun.show()
        
    def initComponent(self):
        self.comNetorchestrDataFun = ComNetorchestrDataFun('NetOrchestrDataFun',
                                                           **{"fileSelect_lineEdit":self.fileSelect_lineEdit,
                                                              "fileSelect_bushbutton":self.fileSelect_bushbutton})
        
        self.comNetorchestrShowFun = ComNetorchestrShowFun('NetOrchestrShowFun',
                                                           **{"pltboard_widget":self.pltboard_widget,
                                                              "timeProcessSpeed_label":self.timeProcessSpeed_label,
                                                              "timeProcessCurrentTime_label":self.timeProcessCurrentTime_label,
                                                              "timeProcess_slider":self.timeProcess_slider,
                                                              "timeProcessPlay_button":self.timeProcessPlay_button,
                                                              "timeProcessRewind_button":self.timeProcessRewind_button,
                                                              "timeProcessFastRewind_button":self.timeProcessFastRewind_button,
                                                              "timeProcessForward_button":self.timeProcessForward_button,
                                                              "timeProcessFastForward_button":self.timeProcessFastForward_button,
                                                              "datatype_choose_comboBox":self.datatype_choose_comboBox})
        
        self.comNetorchestrCalFun = ComNetorchestrCalFun('NetorchestrCalFun', parent=self, 
                                                         **{"mainwindow_menubar":self.menuBar()})
        
        self.comNetorchestrEventFun = ComNetorchestrEventFun('NetorchestrEventFun', parent=self,
                                                             **{"mainwindow_menubar":self.menuBar()})
    
    def ready(self):
        self.comNetorchestrDataFun.data_ready_signal.connect(self.ready_for_show)
        
        self.comNetorchestrShowFun.devPltMap.ctl_set_background_color(self.plt_background_color)
        self.comNetorchestrShowFun.data_type_changed_signal.connect(self.data_type_changed)
        
        self.comNetorchestrCalFun.signal_calculate_aim_changed.connect(self.update_calculate_input)
        

    @pyqtSlot()
    def ready_for_show(self):
        logging.info(f"Ready for show with time series: {self.comNetorchestrDataFun.data_resource_timeseries}")
        self.comNetorchestrShowFun.devTimeProcess.ctl_set_time_series(self.comNetorchestrDataFun.data_resource_timeseries)
        self.comNetorchestrShowFun.devTimeProcess.ctl_set_handle_by_time(self.update_pltboard_handle)

        self.comNetorchestrEventFun.ctl_get_deploy_file_path(self.comNetorchestrDataFun.data_resourse_file_path)
        self.comNetorchestrCalFun.ctl_update_combox([mobility_model.name.split("_")[0] 
                                                     for mobility_model in self.comNetorchestrDataFun.data_node_mobility_list])
        
        # 首次加载数据时，默认绘制第一个时间点
        self.update_pltboard_handle(self.comNetorchestrDataFun.data_resource_timeseries[0])

    @pyqtSlot()
    def data_type_changed(self):
        if len(self.comNetorchestrShowFun.devTimeProcess.time_series) == 0:
            logging.error("资源数据为空，无法更新图形，请先选择文件并加载数据！")
            return
        current_time = self.comNetorchestrShowFun.devTimeProcess.time_series[self.comNetorchestrShowFun.devTimeProcess.current_time_index]
        self.comNetorchestrShowFun.devPltMap.ctl_clear_overlay()
        self.update_pltboard_handle(current_time)
        

    @pyqtSlot()
    def update_calculate_input(self):
        if len(self.comNetorchestrDataFun.data_node_mobility_list) == 0:
            logging.error("资源数据为空，无法更新图形，请先选择文件并加载数据！")
            return
        
        if self.comNetorchestrCalFun.point_1_comboBox.currentText() not in ["None",""]:
            point_1_name = self.comNetorchestrCalFun.point_1_comboBox.currentText()
            point_1_mobility_model = self.comNetorchestrDataFun.ctl_get_mobility_model(point_1_name)
            self.comNetorchestrCalFun.point_1_lon_lineEdit.setText(str(point_1_mobility_model.current_gps[0]))
            self.comNetorchestrCalFun.point_1_lat_lineEdit.setText(str(point_1_mobility_model.current_gps[1]))
            self.comNetorchestrCalFun.point_1_alt_lineEdit.setText(str(point_1_mobility_model.current_gps[2]))
            self.comNetorchestrCalFun.point_1_lon_lineEdit.setCursorPosition(0)
            self.comNetorchestrCalFun.point_1_lat_lineEdit.setCursorPosition(0)
            self.comNetorchestrCalFun.point_1_alt_lineEdit.setCursorPosition(0)

        if self.comNetorchestrCalFun.point_2_comboBox.currentText() not in ["None",""]:
            point_2_name = self.comNetorchestrCalFun.point_2_comboBox.currentText()
            point_2_mobility_model = self.comNetorchestrDataFun.ctl_get_mobility_model(point_2_name)
            self.comNetorchestrCalFun.point_2_lon_lineEdit.setText(str(point_2_mobility_model.current_gps[0]))
            self.comNetorchestrCalFun.point_2_lat_lineEdit.setText(str(point_2_mobility_model.current_gps[1]))
            self.comNetorchestrCalFun.point_2_alt_lineEdit.setText(str(point_2_mobility_model.current_gps[2]))
            self.comNetorchestrCalFun.point_2_lon_lineEdit.setCursorPosition(0)
            self.comNetorchestrCalFun.point_2_lat_lineEdit.setCursorPosition(0)
            self.comNetorchestrCalFun.point_2_alt_lineEdit.setCursorPosition(0)
            
        self.comNetorchestrCalFun.ctl_calculate_start()
        
        
    def update_event_show(self, event_time:str):
        self.comNetorchestrEventFun.ctl_update_show_event(event_time)
        

    def update_pltboard_handle(self, current_time):
        logging.info(f"Update pltboard handle with current time: {current_time}")
                
        self.comNetorchestrShowFun.devTimeProcess.current_time_label.setText(f"仿真天文时长: {DataAnalysis.format_milliseconds(current_time.value)} | 仿真时长：{current_time}")
        resource_load_type = self.comNetorchestrShowFun.datatype_choose_comboBox.currentText()
        resource_load_colors = self.comNetorchestrDataFun.ctl_get_nodes_load_colors(current_time, resource_load_type)
        
        for mobility_model in self.comNetorchestrDataFun.data_node_mobility_list:
            mobility_model.update_current_gps(current_time)

            # 有的节点可能没有资源数据，因此需要单独处理
            if resource_load_colors.get(mobility_model.name.split("_")[0]) is None:
                resource_load_colors[mobility_model.name.split("_")[0]] = "gray"
                continue

            self.comNetorchestrShowFun.devPltMap.ctl_preadd_scatter(mobility_model.name.split("_")[0]+"_scatter",
                                                                    mobility_model.current_gps[0], 
                                                                    mobility_model.current_gps[1], 
                                                                    s=400, alpha=0.7, 
                                                                    color=resource_load_colors[mobility_model.name.split("_")[0]])

            self.comNetorchestrShowFun.devPltMap.ctl_preadd_text(mobility_model.name.split("_")[0]+"_text",
                                                                 mobility_model.current_gps[0], 
                                                                 mobility_model.current_gps[1], 
                                                                 mobility_model.name.split("_")[0], 
                                                                 ha="center", va="center", fontsize=15)
            
        self.comNetorchestrShowFun.devPltMap.ctl_refresh_softly()
        
        
        self.update_event_show(current_time.value)
        
        self.update_calculate_input()
