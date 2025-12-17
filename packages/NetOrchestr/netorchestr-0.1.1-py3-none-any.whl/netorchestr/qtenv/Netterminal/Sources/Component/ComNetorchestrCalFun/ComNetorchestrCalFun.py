
import os

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog, QMenuBar, QAction

from netorchestr.envir.mobility import MobilityBase

from Netterminal.Sources.Component.ComBaseFun import ComBaseFun
from Netterminal.Sources.Component.ComNetorchestrCalFun.Forms import Ui_Dialog_ComNetorchestrCalFun

class ComNetorchestrCalFun(QDialog, Ui_Dialog_ComNetorchestrCalFun, ComBaseFun):
    signal_calculate_aim_changed = pyqtSignal()
    
    def __init__(self, name, parent=None, **kwargs):
        super().__init__(parent)
        ComBaseFun.__init__(self, name)
        self.setupUi(self)
        
        sources_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        style_file_path = os.path.join(sources_dir,'Style', 'MaterialDark.qss')
        with open(style_file_path, 'r', encoding="utf-8") as f:
            qssStyle = f.read()
        self.setStyleSheet(qssStyle)
        
        self.setWindowTitle('NetOrchestr 距离计算器')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(1000, 400)
        
        self.register(**kwargs)
        self.ready()
        
    def register(self, **kwargs):
        self.mainwindow_manubar:QMenuBar = kwargs.get("mainwindow_menubar")
    
    def ready(self):
        # 创建工具菜单栏以及计算器功能按键
        tool_menu = None
        for menu in self.mainwindow_manubar.findChildren(type(self.mainwindow_manubar.addMenu(""))):
            if menu.title() == "工具":
                tool_menu = menu
                break
        if tool_menu is None:
            tool_menu = self.mainwindow_manubar.addMenu("工具")
        
        calculator_action = QAction("距离计算器", self)
        calculator_action.setStatusTip("打开NetOrchestr距离计算器")
        calculator_action.triggered.connect(self.show)
        tool_menu.addAction(calculator_action)
        self.mainwindow_manubar.addSeparator()
        
        
        self.point_1_comboBox.addItem("None")
        self.point_2_comboBox.addItem("None")
        self.point_1_comboBox.currentIndexChanged.connect(self.ctl_update_point_1_lon_lat_lineEdit)
        self.point_2_comboBox.currentIndexChanged.connect(self.ctl_update_point_2_lon_lat_lineEdit)
        
        
        self.calculate_start_pushButton.clicked.connect(self.ctl_calculate_start)
        
        
    def ctl_update_combox(self,choice_list:list[str]):
        self.point_1_comboBox.clear()
        self.point_2_comboBox.clear()
        self.point_1_comboBox.addItems(["None"]+choice_list)
        self.point_2_comboBox.addItems(["None"]+choice_list)
    
    
    @pyqtSlot()
    def ctl_update_point_1_lon_lat_lineEdit(self):
        self.signal_calculate_aim_changed.emit()
    
    @pyqtSlot()
    def ctl_update_point_2_lon_lat_lineEdit(self):
        self.signal_calculate_aim_changed.emit()
        
    @pyqtSlot()
    def ctl_calculate_start(self):
        def check_input(value_str, name, min_val, max_val):
            """
            检查输入是否有效
            :param value_str: 输入框文本
            :param name: 字段名称 (如“经度1”)
            :param min_val: 最小值范围
            :param max_val: 最大值范围
            :return: (是否有效, 转换后的值/错误信息)
            """
            # 非空检查
            if not value_str.strip():
                return False, f"{name}不能为空"
            # 格式检查（是否为数字）
            try:
                value = float(value_str)
            except ValueError:
                return False, f"{name}格式错误，请输入数字"
            # 范围检查
            if not (min_val <= value <= max_val):
                return False, f"{name}超出范围（{min_val} ~ {max_val}）"
            return True, value

        # 2. 检查所有输入（按字段定义范围）
        # 检查点1
        valid, point_1_lon = check_input(
            self.point_1_lon_lineEdit.text(), 
            "经度1", 
            -180, 180
        )
        if not valid:
            return

        valid, point_1_lat = check_input(
            self.point_1_lat_lineEdit.text(), 
            "纬度1", 
            -90, 90
        )
        if not valid:
            return

        valid, point_1_alt = check_input(
            self.point_1_alt_lineEdit.text(), 
            "高度1", 
            -1000, 10000  # 示例范围，可根据实际需求调整
        )
        if not valid:
            return

        # 检查点2
        valid, point_2_lon = check_input(
            self.point_2_lon_lineEdit.text(), 
            "经度2", 
            -180, 180
        )
        if not valid:
            return

        valid, point_2_lat = check_input(
            self.point_2_lat_lineEdit.text(), 
            "纬度2", 
            -90, 90
        )
        if not valid:
            return

        valid, point_2_alt = check_input(
            self.point_2_alt_lineEdit.text(), 
            "高度2", 
            -1000, 10000
        )
        if not valid:
            return

        # 3. 所有输入有效，执行计算
        distance = MobilityBase.calculate_distance(
            [point_1_lon, point_1_lat, point_1_alt],
            [point_2_lon, point_2_lat, point_2_alt]
        )
        
        # 4. 显示结果（可格式化显示，如保留2位小数）
        self.calculate_result_lineEdit.setText(f"{distance:.4f}")
        
        
    