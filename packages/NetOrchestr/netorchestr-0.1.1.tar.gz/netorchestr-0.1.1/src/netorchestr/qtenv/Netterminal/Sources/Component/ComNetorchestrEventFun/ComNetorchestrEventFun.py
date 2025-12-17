
import os
import logging
import pandas as pd

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog, QMenuBar, QAction

from Netterminal.Sources.Component.ComBaseFun import ComBaseFun
from Netterminal.Sources.Component.ComNetorchestrEventFun.Forms import Ui_Dialog_ComNetorchestrEventFun

class ComNetorchestrEventFun(QDialog, Ui_Dialog_ComNetorchestrEventFun, ComBaseFun):
    def __init__(self, name, parent=None, **kwargs):
        super().__init__(parent)
        ComBaseFun.__init__(self, name)
        self.setupUi(self)
       
        sources_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        style_file_path = os.path.join(sources_dir,'Style', 'MaterialDark.qss')
        with open(style_file_path, 'r', encoding="utf-8") as f:
            qssStyle = f.read()
        self.setStyleSheet(qssStyle)
        
        self.setWindowTitle('NetOrchestr MANO 编排日志')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(1000, 400)
        
        self.data_deploy_file_path = None
        
        self.register(**kwargs)
        self.ready()
    
    def register(self, **kwargs):
        self.mainwindow_manubar:QMenuBar = kwargs.get("mainwindow_menubar")
        
    def ready(self):
        # 创建窗口菜单栏以及计算器功能按键
        tool_menu = None
        for menu in self.mainwindow_manubar.findChildren(type(self.mainwindow_manubar.addMenu(""))):
            if menu.title() == "窗口":
                tool_menu = menu
                break
        if tool_menu is None:
            tool_menu = self.mainwindow_manubar.addMenu("窗口")
        
        calculator_action = QAction("MANO 编排日志", self)
        calculator_action.setStatusTip("打开NetOrchestr MANO 编排日志窗口")
        calculator_action.triggered.connect(self.show)
        tool_menu.addAction(calculator_action)
        self.mainwindow_manubar.addSeparator()

    def ctl_get_deploy_file_path(self, resource_file_path:str):
        # 定位仿真结果文件位置
        self.data_result_dir_path  = os.path.dirname(resource_file_path)
        self.data_resource_file_name = os.path.basename(resource_file_path)
        self.data_deploy_file_name = self.data_resource_file_name.replace('resource', 'deploy')
        self.data_deploy_file_path = os.path.join(self.data_result_dir_path, self.data_deploy_file_name)
        
        if not os.path.exists(self.data_deploy_file_path):
            logging.error(f"{self.__class__.__name__}:file {self.data_deploy_file_path} not exist")
            return
    
    def ctl_update_show_event(self, event_time:str):
        self.ctl_clear_event()
        
        if self.data_deploy_file_path is None:
            self.ctl_write_event(f"未找到 MANO 编排日志")
            return
        
        try:
            # 读取CSV文件
            self.data_deploy_df = pd.read_csv(self.data_deploy_file_path)
            
            # 筛选出Time等于event_time的所有行
            matched_rows = self.data_deploy_df[self.data_deploy_df["Time"] == event_time]
            
            if matched_rows.empty:
                self.ctl_write_event(f"未找到 Time 为'{event_time}'的记录")
            else:
                for idx, row in matched_rows.iterrows():
                    # 标题行
                    self.ctl_write_event(f"\n===== 匹配到Time='{event_time}'的记录（行索引{idx}） =====")
                    # 逐字段格式化输出
                    for col, val in row.items():
                        self.ctl_write_event(f"  {col}: {val}")
                    # 结束分隔线
                    self.ctl_write_event("===========================================\n")
        
        except Exception as e:
            # 捕获读取文件或处理时的异常（如文件格式错误）
            self.ctl_write_event(f"处理CSV文件失败: {str(e)}")
        

    def ctl_write_event(self, event_str:str):
        self.eventshow_textBrowser.append(event_str)
        self.eventshow_textBrowser.verticalScrollBar().setValue(0)
        
    def ctl_clear_event(self):
        self.eventshow_textBrowser.clear()


