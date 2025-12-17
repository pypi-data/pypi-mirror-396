#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
"""
omessage.py
============

.. module:: netorchestr.envir.base.omessage
  :platform: Windows
  :synopsis: 消息模块，为离散事件仿真提供标准化的消息实体与数据包封装类。

.. moduleauthor:: WangXi

简介
----

该模块实现了**离散事件仿真中模块间通信消息的标准化封装**功能，主要用于**网络编排（NetOrchestr）** 应用程序中。
它基于 Python 数据类（dataclass）实现消息/数据包的结构化管理，支持消息生存时间（TTL）、内存占用计算、数据序列化等核心能力，是模块间异步通信的基础载体。

核心特性
--------

- 使用 dataclass 组件实现消息/数据包的轻量化封装（自动生成 __init__/__repr__ 等方法）
- 支持消息内存占用计算、TTL 生存时间管理、数据序列化（asdict）等基础控制操作（如消息长度计算、IPv4/Srv4 数据包封装、字段校验等）。
- 与 OGate/OLink 模块联动，作为链路传输的核心数据载体

版本记录
--------

- 版本 1.0 (2025/07/11): 初始版本，实现 OMessage 基础消息类、IPv4Pkt/Srv4Pkt 数据包封装类
"""

import sys
from dataclasses import dataclass, asdict
from astropy import units as u

@dataclass
class OMessage:
    """
    核心消息类，用于离散事件仿真中模块间传输的标准化消息实体。

    该类基于 dataclass 实现，封装了消息的元数据（时间戳、收发方、ID）、内容、生存时间（TTL）等核心字段，
    支持内存占用计算、数据序列化等功能，是 NetOrchestr 框架中通信的最小数据单元。

    Attributes:
        timestamp: 消息发送的时间戳，建议格式为 "YYYY-MM-DD HH:MM:SS.ms"（如 "2025-07-11 10:00:00.123"）
        sender: 消息发送方名称，格式为「模块名_门名」（如 "core_module_gate01"）
        receiver: 消息接收方名称，格式同 sender
        content: 消息内容，支持任意字符串（可封装 JSON 格式的结构化数据）
        id: 消息唯一标识符，建议使用 UUID（如 str(uuid.uuid4())）
        ttl: 消息生存时间（Time-To-Live），单位为毫秒（ms），字符串格式的数字，
             默认为 sys.maxsize（超大值，表示永不过期）
    """
    timestamp: str
    sender: str
    receiver: str
    content: str
    id: str
    ttl: str = str(sys.maxsize)
    
    def __len__(self) -> int:
        """
        计算消息对象的总内存占用（字节），包含自身及所有字段的内存消耗。

        递归计算容器类型（list/dict）的内存占用，确保统计完整，适用于仿真中资源消耗分析。

        Returns:
            int: 消息对象占用的总内存空间大小（字节）

        Example:
            >>> msg = OMessage(
            ...     timestamp="2025-07-11 10:00:00.123",
            ...     sender="core_module",
            ...     receiver="terminal_module",
            ...     content="test message",
            ...     id=str(uuid.uuid4())
            ... )
            >>> print(f"消息内存占用: {len(msg)} 字节")
            消息内存占用: 896 字节
        """
        
        # 对象自身的内存占用
        size = sys.getsizeof(self)
        
        # 获取所有字段的值并计算它们的内存占用
        for value in asdict(self).values():
            # 基本类型（如float、str）的内存占用
            size += sys.getsizeof(value)
            
            # 如果是容器类型（如list、dict），递归计算其元素的内存占用
            if isinstance(value, list):
                for item in value:
                    size += sys.getsizeof(item)
            elif isinstance(value, dict):
                for k, v in value.items():
                    size += sys.getsizeof(k) + sys.getsizeof(v)
        
        return size


@dataclass
class Ipv4Pkt:
    """
    IPv4 数据包封装类，标准化 IPv4 协议数据包的结构。

    用于在 OMessage 的 content 字段中封装 IPv4 格式的数据，适配网络仿真中 IPv4 通信场景。

    Attributes:
        src_ip: 源 IP 地址，格式为 "xxx.xxx.xxx.xxx"（如 "192.168.1.1"）
        dst_ip: 目的 IP 地址，格式同 src_ip
        payload: IP 数据包载荷，字符串格式（可封装应用层数据）
    """
    src_ip: str
    dst_ip: str
    payload: str


@dataclass
class Srv4Pkt:
    """
    Srv4 分段数据包封装类，支持大数据包的分段传输。

    适配网络仿真中超过 MTU（最大传输单元）的数据包分段场景，记录分段剩余数量、分段列表等信息。

    Attributes:
        src_ip: 源 IP 地址，格式为 "xxx.xxx.xxx.xxx"
        dst_ip: 目的 IP 地址，格式同 src_ip
        segment_left: 剩余未传输的分段数量，非负整数
        segment_list: 分段 ID 列表，每个元素为分段的唯一标识（字符串）
        payload: 当前分段的载荷内容，字符串格式
    """
    src_ip: str
    dst_ip: str
    segment_left: int
    segment_list: list[str]
    payload: str

