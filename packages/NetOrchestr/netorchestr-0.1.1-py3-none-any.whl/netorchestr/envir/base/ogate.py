#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
"""
ogate.py
=========

.. module:: netorchestr.envir.base.ogate
  :platform: Windows
  :synopsis: 门模块，用于实现链路与模块之间的通信功能。

.. moduleauthor:: WangXi

简介
----

该模块实现了**模块间链路通信管控**的核心功能，主要用于**网络编排（NetOrchestr）** 应用程序中。
它基于 simpy 仿真框架实现消息的异步传输与缓冲，是模块间数据交互的核心组件。

核心特性
--------

- 使用 simpy.Store 组件实现消息的安全缓冲与异步存取
- 支持门对象的激活、消息入队等基础控制操作（如 put 消息、事件调度、日志记录等）。
- 与 OModule 模块深度耦合，作为模块对外通信的唯一入口

版本记录
--------

- 版本 1.0 (2025/07/11): 初始版本，实现门对象的基础初始化、激活与消息放入功能
"""

from typing import TYPE_CHECKING
from netorchestr.eventlog import OLogger

if TYPE_CHECKING:
    from netorchestr.envir.base import OModule

import simpy


class OGate():
    """门类（OGate），作为链路与模块之间的通信网关。

    该类是 NetOrchestr 框架中模块间通信的核心组件，负责承接链路传输的消息，
    通过 simpy 仿真环境实现消息的异步缓冲与调度，确保模块间通信的有序性。

    Attributes:
        name: 门的唯一标识名称，用于日志与模块内区分不同门实例
        ofModule: 该门所属的模块对象，关联模块上下文
        scheduler: simpy 仿真环境对象，用于事件调度（激活后初始化）
        logger: 日志记录器对象，用于输出门的运行日志（激活后初始化）
        msg_buffer: 消息缓冲区，基于 simpy.Store 实现异步消息存储（激活后初始化）
    """

    def __init__(self, name: str, ofModule: "OModule"):
        """初始化门对象

        Args:
            name: 门的唯一名称，建议格式为「模块名_门类型_序号」（如 "core_module_gate_01"）
            ofModule: 该门所属的 OModule 实例，用于关联模块上下文

        Example:
            >>> from netorchestr.envir.base import OModule
            >>> module = OModule("core_module")
            >>> gate = OGate("core_gate", module)
            >>> print(gate.name)
            core_gate
        """
        
        self.name = name
        """str: 门的唯一标识名称"""
        
        self.ofModule = ofModule
        """OModule: 所属模块对象，关联模块上下文"""
        
        # 延迟初始化的属性（激活后赋值）
        self.scheduler: simpy.Environment | None = None
        """simpy.Environment | None: simpy 事件调度对象，激活前为 None"""

        self.logger: OLogger | None = None
        """OLogger | None: 日志记录器对象，激活前为 None"""

        self.msg_buffer: simpy.Store | None = None
        """simpy.Store | None: 消息缓冲区，基于 simpy.Store 实现，激活前为 None"""
        
        
    def _activate(self, scheduler: simpy.Environment, logger):
        """激活门对象，初始化调度器、日志器与消息缓冲区

        该方法是门对象可用的前提，需在创建实例后调用，完成核心资源的初始化。
        激活后，门才能接收和缓冲消息。

        Args:
            scheduler: simpy 仿真环境实例，用于管理消息的异步调度
            logger: 日志记录器实例，用于输出门的运行状态（如激活日志、消息入队日志）

        Raises:
            ValueError: 若重复调用激活方法（scheduler 已初始化），抛出异常避免重复初始化

        Example:
            >>> import simpy
            >>> import logging
            >>> scheduler = simpy.Environment()
            >>> logger = logging.getLogger("netorchestr")
            >>> gate.activate(scheduler, logger)
            0: Gate core_gate activated.
        """
        
        if self.scheduler is not None:
            raise ValueError(f"Gate {self.name} 已激活，禁止重复调用 activate 方法")

        logger.info(f"{scheduler.now}: Gate {self.name} activated.")

        self.scheduler = scheduler
        self.logger = logger
        self.msg_buffer = simpy.Store(self.scheduler)  # 初始化消息缓冲区
        

    def put(self, msg):
        """向门的消息缓冲区放入消息

        消息会被异步存入 simpy.Store 缓冲区，等待模块消费。
        该方法返回 simpy.Event 对象，可用于监听消息是否成功入队。

        Args:
            msg: 待传输的消息对象，支持任意类型（建议封装为统一的 Message 类）

        Returns:
            simpy.Event: 消息入队事件，可通过该事件监听入队完成状态

        Raises:
            RuntimeError: 若门未激活（msg_buffer 未初始化），抛出异常

        Example:
            >>> msg = {"type": "data", "content": "hello"}
            >>> put_event = gate.put(msg)
            >>> scheduler.run(until=put_event)
            >>> print(gate.msg_buffer.items)
            [{"type": "data", "content": "hello"}]
        """
        if self.msg_buffer is None:
            raise RuntimeError(f"Gate {self.name} 未激活，请先调用 activate 方法")
        
        return self.msg_buffer.put(msg)
        


