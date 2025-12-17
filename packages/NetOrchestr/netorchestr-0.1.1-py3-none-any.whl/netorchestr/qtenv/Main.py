#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
main.py
=======

.. module:: Netterminal.Sources.main
  :platform: Windows, Linux
  :synopsis: Netterminal 网络终端应用程序入口模块，启动 NetOrchestr 可视化界面核心流程。
  
.. moduleauthor:: WangXi

...

'''

import os
import sys
from PyQt5.QtWidgets import QApplication

from Netterminal.Sources.App import AppNetorchestr

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    appNetorchestr = AppNetorchestr()
    appNetorchestr.show()

    sys.exit(app.exec_())
    