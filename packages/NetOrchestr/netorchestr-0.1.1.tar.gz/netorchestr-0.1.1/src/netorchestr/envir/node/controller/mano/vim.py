#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   nfv_vim.py
@Time    :   2024/01/14 21:37:19
@Author  :   Wang Xi
@Version :   0.0
@Contact :   wangxi_chn@foxmail.com
@License :   (C)Copyright 2023-2024, Wang Xi
@Desc    :   None
'''

import numpy as np
import copy
import networkx as nx

from netaddr import IPAddress
from astropy import units as u
from netorchestr.envir.base import OModule
from netorchestr.envir.mobility.base import MobilityBase
from netorchestr.envir.node.ground import GroundServerPlatform
from netorchestr.envir.node.satellite import SatelliteServerPlatform
from netorchestr.envir.node.uav import UavServerPlatform
from netorchestr.envir.node.controller.mano.uem import Ue
from netorchestr.envir.node.controller.mano.vnfm import VnfEm

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from netorchestr.envir.base import ONet
    
class NfvInstance:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.id = kwargs.get('id', None)
        
        self.node_handle: Union[GroundServerPlatform, SatelliteServerPlatform, UavServerPlatform] \
                        = kwargs.get('node_handle', None)

        self.node_type = ""
        """ NFVI 节点所管理的设施平台的类型, 包括 Ground, Sat, Uav """
        if isinstance(self.node_handle, GroundServerPlatform):
            self.node_type = 'Ground'
        elif isinstance(self.node_handle, SatelliteServerPlatform):
            self.node_type = 'Sat'
        elif isinstance(self.node_handle, UavServerPlatform):
            self.node_type = 'Uav'
        else:
            raise ValueError(f"{self.name}: Node handle {self.node_handle} is not supported")

        self.deployed_vnf: list[VnfEm] = []
        self.accessed_ue: list[Ue] = []
        
        self.resource_remain: dict[str, float] = {}
    
    def deploy_VNF(self,vnf_em:VnfEm):
        """向 NFVI 节点部署 VNF

        Args:
            vnf_em (VnfEm): vnf 管理单元(需已完成 VNF 节点绑定)

        Raises:
            ValueError: VnfEm 未绑定 VNF 节点，部署失败
        """
        if vnf_em.node_handler == None:
            raise ValueError(f"VnfEm {vnf_em.name} is not bind to any VNF node, deploy on {self.name} failed")
        self.node_handle.deploy_vnf(vnf_em.node_handler)
        self.update_remain_resource()
        self.deployed_vnf.append(vnf_em)
        vnf_em.ip = vnf_em.node_handler.networkLayer.ip_addr
    
    def update_VNF(self,vnf_em:VnfEm):
        """更新 NFVI 节点上部署的 VNF 的参数

        Args:
            vnf_em (VnfEm): vnf 管理单元(需已完成 VNF 节点绑定)

        Raises:
            ValueError: VnfEm 不存在于 NFVI 节点上部署的 VNF 列表，更新失败
        """
        if vnf_em not in self.deployed_vnf:
            raise ValueError(f"VnfEm {vnf_em.name} is not deployed on NFVI node {self.name}, update failed")
        self.node_handle.update_vnf_resource(vnf_em.node_handler)
        
        
    def undeploy_VNF(self,vnf_em:VnfEm):
        if vnf_em not in self.deployed_vnf:
            raise ValueError(f"VnfEm {vnf_em.name} is not deployed on NFVI node {self.name}, undeploy failed")
        self.node_handle.remove_vnf(vnf_em.node_handler)
        self.deployed_vnf.remove(vnf_em)

    def get_deployed_vnfs(self):
        return [vnf_em.name for vnf_em in self.deployed_vnf]
    
    def get_deployed_vnf_with_type(self, vnf_type: str) -> list[VnfEm]:
        """获取 NFVI 节点上部署的指定类型的且支持被共享使用的 VNF

        Args:
            vnf_type (str): VNF 类型

        Returns:
            list[VnfEm]: 部署的指定类型的且支持被共享使用的 VNF 列表
        """
        return [vnf_em for vnf_em in self.deployed_vnf if vnf_em.type == vnf_type and vnf_em.uesd_shared == True]
    
    def access_ue(self,ue:Ue):
        """令 NFVI 接入 UE, 主要为设置 UE 的 IP 地址

        Args:
            ue (Ue): MANO 中的 UE 模型

        Raises:
            ValueError: UE 已接入 NFVI 节点，接入失败

        Returns:
            Ue: 接入成功的 UE 模型
        """
        if ue in self.accessed_ue:
            raise ValueError(f"UE {ue.name} has already accessed NFVI node {self.name}, access failed")

        ue.set_ip(self.node_handle.ip_manager.get_next_available_ip())
        self.accessed_ue.append(ue)
        return ue

    def unaccess_ue(self,ue:Ue):
        """取消 UE 接入 NFVI 节点, 主要为释放 UE 的 IP 地址

        Args:
            ue (Ue): MANO 中的 UE 模型

        Raises:
            ValueError: UE 之前未接入 NFVI 节点，取消接入失败
        """
        if ue not in self.accessed_ue:
            raise ValueError(f"UE {ue.name} has not accessed NFVI node {self.name}, unaccess failed")

        self.node_handle.ip_manager.release_ip(ue.ip)
        self.accessed_ue.remove(ue)

    def get_accessed_ues(self) -> list[str]:
        return [ue.name for ue in self.accessed_ue]
    
    def update_remain_resource(self):
        self.resource_remain = self.node_handle.update_remain_resource()
    
    def get_remain_resource(self):
        """获取 NFVI 节点上剩余的资源量
            
        Returns:
            dict[str, float]: 剩余资源量字典, 包含 cpu, ram, rom
        """
        self.update_remain_resource()
        self.resource_remain = self.node_handle.get_remaining_resource()
        return self.resource_remain
    
    def get_max_resource(self):
        """获取 NFVI 节点上最大的资源量

        Returns:
            dict[str, float]: 最大资源量字典, 包含 cpu, ram, rom
        """
        return self.node_handle.get_max_resource()
    
    def get_remain_bandwidth(self) -> u.Quantity:
        """获取 NFVI 节点上剩余的带宽

        Returns:
            u.Quantity: 剩余带宽
        """
        return self.node_handle.get_remaining_bandwidth()
    
    def get_max_bandwidth(self) -> u.Quantity:
        """获取 NFVI 节点上最大的带宽

        Returns:
            u.Quantity: 最大带宽
        """
        return self.node_handle.get_max_bandwidth()
    
    def set_route(self, aim_ip_addr:IPAddress, ethernet_phy_name:str):
        """设置 NFVI 节点上的路由器设备中的路由表
            
        Args:
            aim_ip_addr (IPAddress): 目标IP地址
            ethernet_phy (EthernetPhy): 与目标IP地址设备所连接的以太网物理层模块的名称
        """
        self.node_handle.switch.set_route(aim_ip_addr, ethernet_phy_name)
        
    def delete_route(self, aim_ip_addr:IPAddress):
        """删除 NFVI 节点上的路由器设备中的路由表

        Args:
            aim_ip_addr (IPAddress): 目标IP地址
        """
        self.node_handle.switch.delete_route(aim_ip_addr)
        
    def get_route(self, aim_ip_addr:IPAddress) -> str:
        """获取 NFVI 节点上的路由器设备中与目标IP地址设备所连接的以太网物理层模块的名称

        Args:
            aim_ip_addr (IPAddress): 目标IP地址

        Returns:
            str: 与目标IP地址设备所连接的以太网物理层模块的名称
        """
        return self.node_handle.switch.get_route(aim_ip_addr)

    def get_radio_ethernet_phy_name(self) -> str:
        """获取 NFVI 节点上的路由器设备与无线设备相连接的以太网物理层模块的名称

        Returns:
            str: 路由器设备的以太网物理层模块的名称
        """
        switch = self.node_handle.switch
        radio = self.node_handle.duAau
        ethernetPhy = switch.ethernetPhyMap.get(radio.networkLayer.ip_addr, None)
        
        return ethernetPhy.name if ethernetPhy is not None else None
    
    def get_transmite_latency(self) -> float:
        """获取 NFVI 节点上无线设备的传输延迟上限

        Returns:
            float: 无线设备的传输延迟上限
        """
        return self.node_handle.duAau.radioPhy.get_transmission_delay()
        

class VnfVim(OModule):
    def __init__(self, name:str, net:"ONet"):
        super().__init__(name)
        
        self.name = name
        self.net = net
        self.nfvi_group: dict[int, NfvInstance] = {}
        """NFVI 实例组, key 为 NFVI 实例 ID, value 为 NFVI 实例对象"""
        
        self.get_all_nfvi_node_info()

    def get_all_nfvi_node_info(self):
        for nfvi_node in self.net.find_modules_with_class((GroundServerPlatform,
                                                           SatelliteServerPlatform,
                                                           UavServerPlatform)):
            nfvi = NfvInstance(name=nfvi_node.name, 
                               id=len(self.nfvi_group), 
                               node_handle=nfvi_node)
            nfvi.update_remain_resource()
            self.nfvi_group[nfvi.id] = nfvi

    def get_net_remain_resource_list(self) -> list[float]:
        """获取网络中各种剩余资源之和列表

        Returns:
            list[float]: 剩余资源列表, 默认顺序为 CPU, RAM, ROM, BAND
        """
        net_remain_resource:list = None
        for nfvi in self.nfvi_group.values():
            if net_remain_resource is None:
                net_remain_resource = copy.deepcopy(list(nfvi.get_remain_resource().values())) + [nfvi.get_remain_bandwidth()]
            else:
                for i,num in enumerate(list(nfvi.get_remain_resource().values()) + [nfvi.get_remain_bandwidth()]):
                    net_remain_resource[i] += num
        return net_remain_resource

    def get_closest_nfvi_node(self, ue: Ue):
        """获取与 UE 最近且可与之通信的 NFVI 节点

        Args:
            ue (Ue): MANO 中的 UE 模型

        Returns:
            NfvInstance: 与 UE 最近且可与之通信的 NFVI 节点, 若不存在则返回 None
        """

        closest_nfvi_id = None
        closest_distance = np.inf * u.km
        for nfvi_id, nfvi in self.nfvi_group.items():
            flag, distance, _ = self.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue.node_handle.radioPhy,
                                                                                                       nfvi.node_handle.duAau.radioPhy)
            
            if flag and distance < closest_distance:
                closest_distance = distance
                closest_nfvi_id = nfvi_id
                
        if closest_nfvi_id is not None:
            return self.nfvi_group[closest_nfvi_id]
        else:
            return None
    
    def get_can_access_nfvi_node(self, ue: Ue) -> list[NfvInstance]:
        """获取可以被 UE 接入的 NFVI 节点列表

        Args:
            ue (Ue): MANO 中的 UE 模型

        Returns:
            list[NfvInstance]: 可以被 UE 接入的 NFVI 节点列表, 若不存在则返回空列表
        """
        
        can_access_nfvi_list:list[NfvInstance] = []
        for nfvi_id, nfvi in self.nfvi_group.items():
            flag, _, _ = self.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue.node_handle.radioPhy,
                                                                                                nfvi.node_handle.duAau.radioPhy)
            
            if flag:
                can_access_nfvi_list.append(nfvi)

        return can_access_nfvi_list
    
    
    def get_latency_between_nfvi_node(self, nfvi_1: NfvInstance, nfvi_2: NfvInstance) -> u.Quantity:       
        nfvi_1_gps, catch_flag = nfvi_1.node_handle.mobiusTraj.update_current_gps(self.scheduler.now*u.ms)
        if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} get_latency_between_nfvi_node need "
                                             f"{nfvi_1.node_handle.name} update current gps: {nfvi_1_gps}")
        
        nfvi_2_gps, catch_flag = nfvi_2.node_handle.mobiusTraj.update_current_gps(self.scheduler.now*u.ms)
        if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} get_latency_between_nfvi_node need "
                                             f"{nfvi_2.node_handle.name} update current gps: {nfvi_2_gps}")
        
        _, _, latency = self.check_neighbour_nfvi_node(nfvi_1, nfvi_2)
        
        return latency
    
    
    def check_neighbour_nfvi_node(self, nfvi_1: NfvInstance, nfvi_2: NfvInstance) -> bool:
        """检查两个 NFVI 节点是否邻接

        Args:
            nfvi_1 (NfvInstance): 需判断的NFVI对象1
            nfvi_2 (NfvInstance): 需判断的NFVI对象2

        Returns:
            bool: True 表示邻接, False 表示不邻接
            
            u.Quantity: 两节点间的距离
            
            u.Quantity: 两节点间的延迟
        """
        if nfvi_1 == nfvi_2:
            return True, 0 * u.km, 1 * u.ms
          
        if nfvi_1.node_type == "Sat" and nfvi_2.node_type == "Sat":
            # 卫星间的激光束通信的邻接判断需单独处理
            nfvi_aim_lasers_aim_ip = [laser.aim_laser_ip for laser in nfvi_1.node_handle.laser_group]
            nfvi_node_lasers_ip = [laser.networkLayer.ip_addr for laser in nfvi_2.node_handle.laser_group]
            if not any(ip in nfvi_node_lasers_ip for ip in nfvi_aim_lasers_aim_ip):
                return False, np.inf * u.km, np.inf * u.ms
            else:
                nfvi_1_gps = nfvi_1.node_handle.mobiusTraj.current_gps
                nfvi_2_gps = nfvi_2.node_handle.mobiusTraj.current_gps
                distance = MobilityBase.calculate_distance(nfvi_1_gps, nfvi_2_gps)
                light_speed = 3e8 * u.m / u.s
                latency = distance / light_speed
                
                return True, distance, latency
        else:
            flag, distance, latency = self.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(nfvi_1.node_handle.duAau.radioPhy,
                                                                                                             nfvi_2.node_handle.duAau.radioPhy)
            return flag, distance, latency
        
    
    def get_neighbour_nfvi_node(self, nfvi_aim: NfvInstance, time: u.Quantity = None):
        """获取与 NFVI 节点邻接的 NFVI 节点

        Args:
            nfvi_aim (NfvInstance): NFVI 实例对象
            time (u.Quantity, optional): 仿真开始后经历的时长. Defaults to None. 如果为 None, 则默认为当前仿真时间.

        Returns:
            list[NfvInstance]: 与 NFVI 节点邻接的 NFVI 节点列表
            
            list[u.Quantity]: 与 NFVI 节点邻接的 NFVI 节点的距离列表
            
            list[u.Quantity]: 与 NFVI 节点邻接的 NFVI 节点的延迟列表
        """
        if time == None:
            time = self.scheduler.now*u.ms
        
        neighbour_nfvi_list:list[NfvInstance] = []
        neighbour_nfvi_distance_list:list[u.Quantity] = []
        neighbour_nfvi_latency_list:list[u.Quantity] = []
        
        nfvi_aim_gps, catch_flag = nfvi_aim.node_handle.mobiusTraj.update_current_gps(time)
        if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} get_neighbour_nfvi_node "
                                             f"need {nfvi_aim.node_handle.name} update current gps: {nfvi_aim_gps}")
        
        for nfvi_id, nfvi_node in self.nfvi_group.items():
            if nfvi_id == nfvi_aim.id:
                continue
            nfvi_node_gps, catch_flag = nfvi_node.node_handle.mobiusTraj.update_current_gps(time)
            if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} get_neighbour_nfvi_node "
                                                 f"need {nfvi_node.node_handle.name} update current gps: {nfvi_node_gps}")
            
            if nfvi_aim.node_type == "Sat" and nfvi_node.node_type == "Sat":
                # 卫星间的激光束通信的邻接判断需单独处理
                nfvi_aim_lasers_aim_ip = [laser.aim_laser_ip for laser in nfvi_aim.node_handle.laser_group]
                nfvi_node_lasers_ip = [laser.networkLayer.ip_addr for laser in nfvi_node.node_handle.laser_group]
                if any(ip in nfvi_node_lasers_ip for ip in nfvi_aim_lasers_aim_ip):
                    neighbour_nfvi_list.append(nfvi_node)
                    distance = MobilityBase.calculate_distance(nfvi_aim_gps, nfvi_node_gps)
                    light_speed = 3e8 * u.m / u.s
                    latency = distance / light_speed
                    neighbour_nfvi_distance_list.append(distance)
                    neighbour_nfvi_latency_list.append(latency)
            else:
                flag, distance, latency = self.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(nfvi_aim.node_handle.duAau.radioPhy,
                                                                                                                 nfvi_node.node_handle.duAau.radioPhy)
                if flag:
                    neighbour_nfvi_list.append(nfvi_node)
                    neighbour_nfvi_distance_list.append(distance)
                    neighbour_nfvi_latency_list.append(latency)
                    
        return neighbour_nfvi_list, neighbour_nfvi_distance_list, neighbour_nfvi_latency_list
    
    
    def get_adjacent_matrix(self, time: u.Quantity = None) -> np.ndarray:
        """获取网络中各 NFVI 节点间构成的邻接矩阵
        
        Args:
            time (u.Quantity, optional): 仿真开始后经历的时长. Defaults to None. 如果为 None, 则默认为当前仿真时间.

        Returns:
            np.ndarray: 邻接矩阵, 元素为 1 表示有邻接, 0 表示无邻接, 默认对角元素为 1
        """
        if time == None:
            time = self.scheduler.now*u.ms
        
        num_node = len(self.nfvi_group)
        adjacent_matrix = np.eye(num_node)
        
        for nfvi_aim in self.nfvi_group.values():
            neighbour_nfvi_list, _, _ = self.get_neighbour_nfvi_node(nfvi_aim, time)
            for nfvi_neighbour in neighbour_nfvi_list:
                adjacent_matrix[nfvi_aim.id][nfvi_neighbour.id] = 1
                adjacent_matrix[nfvi_neighbour.id][nfvi_aim.id] = 1
        return adjacent_matrix
    
    
    def get_graph(self, time: u.Quantity = None, with_weight:str="None") -> nx.Graph:
        """获取网络中各 NFVI 节点间构成的图

        Args:
            time (u.Quantity, optional): 仿真开始后经历的时长. Defaults to None. 如果为 None, 则默认为当前仿真时间.
        
            with_weight (str, optional): 使用权重. 可以设置为 "None" / "Distance" / "Latency". Defaults to “None”.

        Returns:
            nx.Graph: 图对象, 节点为 NFVI 实例 ID, 边为邻接关系, 若 with_weight 为 True, 则边权重为距离或时延
        
        Example:
            >>> vnf_vim = VnfVim("VnfVim", net)
            >>> graph = vnf_vim.get_graph(time=self.scheduler.now*u.ms, withWeight="Distance")
            >>> nx.draw(graph, with_labels=True)
            >>> plt.show()
        
        """
        if time == None:
            time = self.scheduler.now*u.ms
        
        if with_weight == "None":
            return nx.from_numpy_array(self.get_adjacent_matrix(time), create_using=nx.Graph)
        elif with_weight == "Distance":
            graph = nx.Graph()
            graph.add_nodes_from([nfvi_aim.id for nfvi_aim in self.nfvi_group.values()])
            
            for nfvi_aim in self.nfvi_group.values():
                neighbour_nfvi_list, neighbour_distance_list, _ = self.get_neighbour_nfvi_node(nfvi_aim, time)
                for j, nfvi_neighbour in enumerate(neighbour_nfvi_list):
                    graph.add_edge(nfvi_aim.id, nfvi_neighbour.id, weight=neighbour_distance_list[j].to(u.km).value)
                    
            # 添加自环
            for nfvi_aim in self.nfvi_group.values():
                graph.add_edge(nfvi_aim.id, nfvi_aim.id, weight=0)
            
            return graph
        elif with_weight == "Latency":
            graph = nx.Graph()
            graph.add_nodes_from([nfvi_aim.id for nfvi_aim in self.nfvi_group.values()])
            
            for nfvi_aim in self.nfvi_group.values():
                neighbour_nfvi_list, _, neighbour_latency_list = self.get_neighbour_nfvi_node(nfvi_aim, time)
                for j, nfvi_neighbour in enumerate(neighbour_nfvi_list):
                    graph.add_edge(nfvi_aim.id, nfvi_neighbour.id, weight=neighbour_latency_list[j].to(u.ms).value)
                    
            # 添加自环
            for nfvi_aim in self.nfvi_group.values():
                graph.add_edge(nfvi_aim.id, nfvi_aim.id, weight=1)
            
            return graph
        else:
            raise ValueError(f"{self.name}: get_graph() 参数 with_weight 参数错误, 请设置为 None / Distance / Latency")
    
    
    def get_graph_to_ue(self, ue: Ue, uesd_graph: nx.Graph, with_weight:str="None") -> nx.Graph:
        """得到一个新的图将用户作为一个节点添加到网络中

        Args:
            ue (Ue): 用户模型
            uesd_graph (nx.Graph): 作为基础的图对象

        Returns:
            nx.Graph: 新增用户节点所得到的图
        """
        ue_node_id = len(uesd_graph.nodes)
        new_graph = copy.deepcopy(uesd_graph)
        new_graph.add_node(ue_node_id)
        
        can_access_nfvi_list = self.get_can_access_nfvi_node(ue)
        if with_weight == "None":
            for nfvi in can_access_nfvi_list:
                new_graph.add_edge(ue_node_id, nfvi.id)
        elif with_weight == "Distance":
            for nfvi in can_access_nfvi_list:
                _, distance, _ = self.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue.node_handle.radioPhy,
                                                                                                        nfvi.node_handle.duAau.radioPhy)
                new_graph.add_edge(ue_node_id, nfvi.id, weight=distance.to(u.km).value)
        elif with_weight == "Latency":
            for nfvi in can_access_nfvi_list:
                _, _, latency = self.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue.node_handle.radioPhy,
                                                                                                        nfvi.node_handle.duAau.radioPhy)
                new_graph.add_edge(ue_node_id, nfvi.id, weight=latency.to(u.ms).value)
        else:
            raise ValueError(f"{self.name}: expand_graph_to_ue() 参数 with_weight 参数错误, 请设置为 None / Distance / Latency")
        
        return new_graph
        

    def draw_graph(self, time: u.Quantity = None, withWeight: str = "None"):
        """绘制当前时刻网络中各 NFVI 节点间构成的图

        Args:
            withWeight (bool, optional): 使用权重. 可以设置为 "None" / "Distance" / "Latency". Defaults to “None”.
        """
        from matplotlib import pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        import os
        
        if time == None:
            time = self.scheduler.now*u.ms
        
        save_id = int(self.scheduler.now)
        save_path = f"TraceNFVI/"
        os.makedirs(save_path, exist_ok=True)
        
        G = self.get_graph(time, withWeight)
        nodes = sorted(G.nodes())  # 按节点ID排序
        n = len(nodes)

        # 初始化邻接矩阵（用0表示无连接，实际可根据需求调整）
        adj_matrix = np.zeros((n, n))
        for i, u in enumerate(nodes):
            for j, v in enumerate(nodes):
                if u != v and G.has_edge(u, v):
                    adj_matrix[i, j] = G[u][v]['weight']

        # 2. 配置灰度映射（权重越大，颜色越深）
        # 自定义灰度 colormap（从白色到黑色）
        gray_cmap = LinearSegmentedColormap.from_list('custom_gray', ['white', 'black'])

        # 3. 绘制灰度矩阵图
        plt.figure(figsize=(8, 6))

        # 绘制热力图（格子图）
        im = plt.imshow(
            adj_matrix, 
            cmap=gray_cmap, 
            interpolation='nearest',  # 不插值，保持格子清晰
            vmin=0,  # 最小值（无连接）
            vmax=np.max(adj_matrix) if np.max(adj_matrix) > 0 else 1  # 最大值（最大权重）
        )

        # 添加颜色条（显示灰度与权重的对应关系）
        cbar = plt.colorbar(im)
        cbar.set_label('Edge Weight', fontsize=12)

        # 配置坐标轴（显示节点ID）
        plt.xticks(range(n), nodes, fontsize=10)
        plt.yticks(range(n), nodes, fontsize=10)
        plt.xlabel('Node', fontsize=12)
        plt.ylabel('Node', fontsize=12)
        plt.title('Gray Scale Matrix Plot of Graph Edges', fontsize=14)

        # 在格子中显示权重值（可选）
        for i in range(n):
            for j in range(n):
                if adj_matrix[i, j] > 0:  # 只显示有连接的权重，红色为较大值，蓝色为较小值
                    plt.text(j, i, f'{adj_matrix[i, j]:.1f}', 
                            ha='center', va='center', 
                            color='red' if adj_matrix[i, j] > np.max(adj_matrix)*0.5 else 'blue')

        plt.tight_layout()
        plt.savefig(f"{save_path}/TraceNFVI_graph_{save_id}.png")
        plt.close()
        
    def who_has_vnf_with_type(self, vnf_type: str) -> list[NfvInstance]:
        """获取当前时刻网络中部署了指定类型的且支持被共享使用的 VNF 的 NFVI 节点

        Args:
            vnf_type (str): VNF 类型

        Returns:
            list[NfvInstance]: 部署了指定类型的且支持被共享使用的 VNF 的 NFVI 节点列表
        """
        nfvi_list = []
        for nfvi in self.nfvi_group.values():
            for vnf_em in nfvi.deployed_vnf:
                if vnf_em.type == vnf_type and vnf_em.uesd_shared == True:
                    nfvi_list.append(nfvi)
                    break
        return nfvi_list
    
    def who_can_route_to_nfvi(self, nfvi_aim: NfvInstance, uesd_graph: nx.Graph) -> list[NfvInstance]:
        """获取当前时刻网络中可以路由到指定 NFVI 节点的 NFVI 节点

        Args:
            nfvi_aim (NfvInstance): 目标 NFVI 节点
            uesd_graph (nx.Graph): 已经构建好的图对象

        Returns:
            list[NfvInstance]: 可以路由到指定 NFVI 节点的 NFVI 节点列表
        """
        nfvi_list = [nfvi_aim]
        for nfvi in self.nfvi_group.values():
            if nfvi.id == nfvi_aim.id:
                continue
            if nx.has_path(uesd_graph, nfvi.id, nfvi_aim.id):
                nfvi_list.append(nfvi)
        return nfvi_list
    
    
    def who_has_most_resource(self, list_nfvi: list[NfvInstance], resource_type: str) -> NfvInstance:
        """获取列表中 NFVI 节点中拥有最多剩余资源的 NFVI 节点

        Args:
            list_nfvi (list[NfvInstance]): 列表中 NFVI 节点
            resource_type (str): 资源类型

        Returns:
            NfvInstance: 列表中 NFVI 节点中拥有最多资源的 NFVI 节点
        """
        max_resource = 0
        max_nfvi = None
        for nfvi in list_nfvi:
            nfvi_resource = nfvi.node_handle.get_remaining_resource().get(resource_type)
            if nfvi_resource >= max_resource:
                max_resource = nfvi_resource
                max_nfvi = nfvi
                
        return max_nfvi
    
    def get_nfvis_name_with_id(self, nfvis_id: list[str]) -> list[str]:
        """根据 NFVI ID 获取 NFVI 名称

        Args:
            nfvis_id (list[str]): NFVI ID 列表

        Returns:
            list[str]: NFVI 名称列表
        """
        nfvis_name = []
        for nfvi_id in nfvis_id:
            if nfvi_id in self.nfvi_group:
                nfvis_name.append(self.nfvi_group[nfvi_id].node_handle.name)
            else:
                nfvis_name.append(None)
        return nfvis_name
    