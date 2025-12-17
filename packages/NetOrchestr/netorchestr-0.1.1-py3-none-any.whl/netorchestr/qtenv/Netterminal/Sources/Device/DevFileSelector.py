#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
DevFileSelector.py
==================

.. module:: Netterminal.Sources.Device.DevFileSelector
  :platform: Windows, Linux
  :synopsis: PyQt5 文件选择器模块，实现系统文件可视化选择、路径编辑与状态通知的标准化功能。

.. moduleauthor:: WangXi

简介
----

该模块实现了**PyQt5 界面下的系统文件选择与路径管理**功能，主要用于**Netterminal 网络终端**应用程序中。
作为 DevBase 的子类，它封装了 QFileDialog 与 QPushButton/QLineEdit 控件的联动逻辑，支持文件可视化选择、路径手动编辑、选择状态信号通知等核心能力，是文件操作类功能的基础组件。

核心特性
--------

- 使用 PyQt5 组件（QPushButton/QLineEdit/QFileDialog）呈现文件选择界面与路径展示
- 支持基本的文件选择控制操作（如可视化选择文件、手动编辑文件路径、路径变更日志记录、选择状态信号发射等）。
- 提供标准化的文件路径设置接口，兼容相对路径/绝对路径，自动格式化路径分隔符

版本
----

- 版本 1.0 (2025/03/31): 初始版本，实现文件选择对话框调用、路径编辑、状态信号通知核心逻辑
'''

import os
import logging
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QFileDialog, QLineEdit

from Netterminal.Sources.Device.DevBase import DevBase

class DevFileSelector(DevBase):
    file_choosed_signal = pyqtSignal()
    def __init__(self,name:str,**kwargs):
        super(DevFileSelector,self).__init__(name)
        
        self.register(**kwargs)
        
        self.file_path = None
        
    
    def register(self,**kwargs):
        self.fileSelect_bushbutton:QPushButton = kwargs.get('fileSelect_bushbutton',None)
        if not isinstance(self.fileSelect_bushbutton, QPushButton):
            raise TypeError("传入的控件必须是 QPushButton 类")
        self.fileSelect_lineEdit:QLineEdit = kwargs.get('fileSelect_lineEdit',None)
        if not isinstance(self.fileSelect_lineEdit, QLineEdit):
            raise TypeError("传入的控件必须是 QLineEdit 类")
        

    def ready(self):
        self.fileSelect_bushbutton.clicked.connect(self.on_open_file_dialog)
        self.fileSelect_lineEdit.editingFinished.connect(self.on_lineEdit_changed)
        
    
    def ctl_set_file_path(self,file_path:str): 
        self.file_path = file_path
        self.fileSelect_lineEdit.setText(file_path)
        logging.info(f"{self.name} | 当前选择文件路径：{self.file_path}")
    
    
    @pyqtSlot()
    def on_open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(None, "选择文件", os.getcwd(), "文本文件 (*.csv);;所有文件 (*)", options=options)
        if file_path:
            self.ctl_set_file_path(os.path.normpath(file_path))
            self.file_choosed_signal.emit()
            
            
    @pyqtSlot()
    def on_lineEdit_changed(self):
        self.ctl_set_file_path(self.fileSelect_lineEdit.text())
        self.file_choosed_signal.emit()

