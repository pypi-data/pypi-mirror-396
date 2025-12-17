#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
'''
node_base.py
============

.. module:: netorchestr.envir.node.base
  :platform: Windows
  :synopsis: 节点模型基类模块，实现网络节点的层级/平级模块连接标准化，是所有业务节点的基础父类。

.. moduleauthor:: WangXi

简介
----

该模块实现了**网络节点内层级模块与平级模块的标准化连接**功能，主要用于**NetOrchestr 网络编排**应用程序中。
作为节点模型的核心基类，它继承自 OModule，提供了通用的模块连接逻辑（层级上下行、平级对等），通过 OGate/OLink 封装节点内部/节点间的通信链路，统一模块交互的拓扑规则。

核心特性
--------

- 使用 OGate/OLink 组件实现模块间的标准化通信链路封装，支持自定义连接延迟
- 支持基本的节点模块拓扑控制操作（如层级模块上下行连接、平级模块对等连接、链路延迟配置等）。
- 定义通用的节点连接规则，子类可直接继承复用，无需重复实现连接逻辑

版本
----

- 版本 1.0 (2025/07/11): 初始版本，实现节点层级/平级模块的标准化连接逻辑
'''

from astropy import units as u
from netorchestr.envir.base import OModule, OLink, OGate

class NodeBase(OModule):
    def __init__(self, name: str):
        """初始化节点模型基类

        Args:
            name (str): 节点名称
        """
        super().__init__(name)
        
    @staticmethod
    def connect_layer_submodules(layer_module_list: list[OModule], link_delay: u.Quantity = 0*u.ms):
        """使用门将各层模块连接起来

        Args:
            layer_module_list (list[OModule]): 按照从顶至下的顺序传入各层模块
            link_delay (u.Quantity, optional): 连接延迟. Defaults to 0*u.ms.
            
        Note:
            模块之间的连接方式为：
            ```
            |-------------|                                  |-------------|
            |    upper   -|-lowerLayerIn-------upperLayerOut-|-   lower    |
            |    module  -|-lowerLayerOut-------upperLayerIn-|-   module   |
            |-------------|                                  |-------------|
            ```
        """
        if len(layer_module_list) <= 1:
            return
        for upper_module_index in range(len(layer_module_list)-1):
            upper_module = layer_module_list[upper_module_index]
            lower_module = layer_module_list[upper_module_index+1]
            
            upper_module_lower_layer_ingate = OGate("lowerLayerIn", upper_module)
            upper_module_lower_layer_outgate = OGate("lowerLayerOut", upper_module)
            lower_module_upper_layer_ingate = OGate("upperLayerIn", lower_module)
            lower_module_upper_layer_outgate = OGate("upperLayerOut", lower_module)
            
            link_1 = OLink(delay=link_delay)
            link_2 = OLink(delay=link_delay)
            
            upper_module.gates[upper_module_lower_layer_ingate] = (link_1, lower_module_upper_layer_outgate)
            upper_module.gates[upper_module_lower_layer_outgate] = (link_2, lower_module_upper_layer_ingate)
            lower_module.gates[lower_module_upper_layer_ingate] = (link_2, upper_module_lower_layer_outgate)
            lower_module.gates[lower_module_upper_layer_outgate] = (link_1, upper_module_lower_layer_ingate)
    
    @staticmethod
    def connect_peer_submodules(peer_module_list: list[OModule], link_delay: u.Quantity = 0*u.ms):
        """使用门将平级模块连接起来

        Args:
            peer_module_list (list[OModule]): 平级模块列表
            link_delay (u.Quantity, optional): 连接延迟. Defaults to 0*u.ms.
            
        Note:
            模块之间的连接方式为：
            ```
            |-------------|                                  |-------------|
            |    module  -|-lowerLayerIn-------lowerLayerOut-|-   module   |
            |      1     -|-lowerLayerOut-------lowerLayerIn-|-     2      |
            |-------------|                                  |-------------|
            ```
            
        """
        if len(peer_module_list) <= 1:
            return
        for module_index in range(len(peer_module_list)-1):
            module1 = peer_module_list[module_index]
            module2 = peer_module_list[module_index+1]
            
            module1_lower_layer_ingate = OGate("lowerLayerIn", module1)
            module1_lower_layer_outgate = OGate("lowerLayerOut", module1)
            module2_lower_layer_ingate = OGate("lowerLayerIn", module2)
            module2_lower_layer_outgate = OGate("lowerLayerOut", module2)
            
            link_1 = OLink(delay=link_delay)
            link_2 = OLink(delay=link_delay)
            
            module1.gates[module1_lower_layer_ingate] = (link_1, module2_lower_layer_outgate)
            module1.gates[module1_lower_layer_outgate] = (link_2, module2_lower_layer_ingate)
            module2.gates[module2_lower_layer_ingate] = (link_2, module1_lower_layer_outgate)
            module2.gates[module2_lower_layer_outgate] = (link_1, module1_lower_layer_ingate)
        
