#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
'''
omodule.py
==========

.. module:: netorchestr.envir.base.omodule
  :platform: Windows
  :synopsis: 核心模块类，实现离散事件仿真中模块的生命周期管理、消息收发、拓扑关联等核心能力。

.. moduleauthor:: WangXi

简介
----

该模块实现了**离散事件仿真中网络节点模块的全生命周期管理**功能，主要用于**网络编排（NetOrchestr）** 应用程序中。
作为框架的核心基类，它整合了门（OGate）、链路（OLink）、消息（OMessage）等组件，提供模块激活、消息收发、拓扑管理（门/链路/子模块）、仿真事件调度等核心能力，是所有业务模块的基础父类。

核心特性
--------

- 使用 simpy 仿真环境组件实现事件调度与资源管控，支撑离散事件的异步处理
- 支持基本的模块拓扑管理操作（如门的增删、链路的关联、子模块的嵌套、消息收发/转发等）。
- 提供模块化扩展能力（如子类重写 recv_msg/update 方法实现自定义业务逻辑）

版本
----

- 版本 1.0 (2025/07/11): 初始版本，实现模块基础初始化、门/链路/子模块管理、消息收发核心逻辑
'''

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netorchestr.eventlog import OLogger
    from netorchestr.envir.base import OMessage
    
from netorchestr.envir.base import OGate, OLink
    
import simpy
import copy
from astropy import units as u

class OModule:
    def __init__(self, name:str):
        """模块定义

        Args:
            name (str): 自定义模块名称
        """
        
        self.name = name
        """模块名称"""
        
        self.gates:dict["OGate",tuple["OLink", "OGate"]] = {}
        """模块的门 'OGate' 与对应的链路模型 'OLink' 和所连接的门 'OGate' 的映射表"""
        
        self.oSubModules:list["OModule"] = []
        """模块的子模块列表"""
        
        self.ofModule:OModule = None
        """模块的父模块"""
                   
        
    def _activate(self, schedule:"simpy.Environment", logger:"OLogger"):
        """激活模块
        
        """
        logger.debug(f"{schedule.now}: Module '{self.name}' is activated")
        
        self.scheduler:"simpy.Environment" = schedule
        """模块的事件调度器"""
        
        self.logger:"OLogger" = logger
        """模块的日志记录器"""
        
        self.req_processor = simpy.Resource(self.scheduler, capacity=1) 
        """simpy 资源处理器, 可用于模拟资源紧张时的消息处理, 默认不使用
        
        Note:
            该资源处理器仅用于模拟资源紧张时的消息处理, 例如实现同一时刻仅能处理一定数量消息的情况
            
            基本用法为：
            
            request = self.processor.request()
            
            with request as req:
                yield req
                
                # process the message
                
                yield self.schedule.timeout(processing_delay)
        """
        
        self.req2msg:dict[simpy.Resource,"OMessage"] = {}
        """simpy 资源请求-消息映射表, 可用来追踪消息处理队列长度, 默认不使用
        
        Note:
            使用时需手动进行保存,这么做的根本原因是 simpy 的 Resource 中为 req 的缓存队列而非 msg 的缓存队列
            
            因此无法获知其中的 msg 的信息, 而我们有时需要对缓存队列中的 msg 进行筛选, 比如获知某类 msg 的待处理数量
            
            这里建立的映射表可用于追踪 req 与 msg 的对应关系, 以便于后续处理
            
            基本用法为：
            
            request = self.processor.request()
            self.req2msg[request] = msg
            
        """
        
        for gate in self.gates:
            gate._activate(self.scheduler, self.logger)
            
        for sub_module in self.oSubModules:
            sub_module._activate(self.scheduler, self.logger)
        
        self.scheduler.process(self.__init())
        
        for gate in self.gates:
            self.scheduler.process(self.__run(gate))
    
    def __init(self):
        """模块初始化
        
        """
        yield self.scheduler.timeout(0)
        self.initialize()
        

    def initialize(self):
        """模块初始化
        
        """
        pass
        
        
    def send_msg(self, msg:"OMessage", gate:"OGate"):
        """发送消息
        
        """
        if gate not in self.gates:
            self.logger.error(f"{self.scheduler.now}: Module '{self.name}' does not have outgate '{gate.name}'")
            return
        
        aim_link:"OLink" = self.gates[gate][0]
        aim_gate:"OGate" = self.gates[gate][1]
        aim_module:"OModule" = aim_gate.ofModule

        self.logger.debug(f"{self.scheduler.now}: Module '{self.name}' sends message '{msg.id}' to module '{aim_module.name}' via outgate '{gate.name}' with delay '{aim_link.delay}'")
        
        self.scheduler.process(self.__deliver_msg(msg, aim_link.delay, aim_gate))
        
    def __deliver_msg(self, message, delay:u.Quantity, aim_gate:"OGate"):
        """私有方法：在传播时延之后将消息副本放入目标模块的门的消息缓存区
        
        """
        
        yield self.scheduler.timeout(delay.to(u.ms).value)
        
        try:
            put_event = aim_gate.msg_buffer.put(copy.deepcopy(message))
        except:
            import sys
            import code
            print("Unexpected error:", sys.exc_info())
            code.interact(local=locals())
        
        yield put_event
        
    def recv_msg(self, msg:"OMessage", in_gate:"OGate"):
        raise NotImplementedError("recv_msg() method should be implemented by subclass")
    
    def activate_gate(self, gate:"OGate"):
        """激活额外增加的门
        
        """
        if gate not in self.gates:
            print(list(self.gates.keys()))
            raise ValueError(f"Module '{self.name}' does not have gate '{gate}'")
        
        gate._activate(self.scheduler, self.logger)
        self.scheduler.process(self.__run(gate))
    
    def add_gate(self, self_gate_name:str, link:"OLink", aim_gate:"OGate"):
        """添加门
        
        """
        
        # add the gate to the gates
        ogate = OGate(self_gate_name, self)
        self.gates[ogate] = (link, aim_gate)
                
    def del_gate(self, gate_name:str):
        """删除门
        
        """
        for gate in self.gates:
            if gate.name == gate_name:
                del self.gates[gate]
                return
            
    def add_link(self, link:"OLink", aim_module:"OModule"):
        """添加链路
        
        """
        self_gate_name = f"{self.name}G{len(self.gates)}"
        aim_gate_name = f"{aim_module.name}G{len(aim_module.gates)}"
        self_gate = OGate(self_gate_name, self)
        aim_gate = OGate(aim_gate_name, aim_module)
        self.gates[self_gate] = (link, aim_gate)
        aim_module.gates[aim_gate] = (link, self_gate)
                
    def del_link(self, aim_module:"OModule"):
        """删除链路
        
        """
        for self_gate in self.gates:
            link, aim_gate = self.gates[self_gate]
            if aim_gate.ofModule == aim_module:
                self.del_gate(self_gate.name)
                aim_module.del_gate(aim_gate.name)
    
    def add_submodule(self, sub_module:"OModule"):
        """添加子模块
        
        """
        self.oSubModules.append(sub_module)
        
    def remove_submodule(self, sub_module:"OModule"):
        """删除子模块
        
        """
        self.oSubModules.remove(sub_module)
    
    def update(self):
        """模块状态更新，被子类继承实现
        
        Args:
            time (float): 当前仿真时间
        
        """
        pass
    
    def find_top_module(self) -> "OModule":
        """查找最顶层的模块
        
        Returns:
            OModule: 最顶层的模块
        """
        def find_top_module_helper(module:"OModule") -> "OModule":
            if module.ofModule is None:
                return module
            else:
                return find_top_module_helper(module.ofModule)
        
        return find_top_module_helper(self)

    
    def __run(self,gate:"OGate"=None):
        """节点的消息处理循环，处理消息接收和响应"""
        while True:
            message:"OMessage" = yield gate.msg_buffer.get()
            self.logger.debug(f"{self.scheduler.now}: Module '{self.name}' receives message "+
                                f"'{message.id}' from module '{self.gates[gate][1].ofModule.name}' "+
                                f"via ingate '{gate.name}' with delay '{self.gates[gate][0].delay}'")
            self.recv_msg(message, gate)
