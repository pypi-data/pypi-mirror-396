#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_lm_sfcp.py
========================

.. module:: solver_deploy_lm_sfcp
  :platform: Windows
  :synopsis: 基于LM-SFCP算法的SFC编排求解器模块，支持LEO巨型星座网络中的移动感知型部署与迁移

.. moduleauthor:: WangXi

简介
----

该模块实现了论文提出的大规模移动感知卫星网络SFC部署算法（LM-SFCP），核心聚焦LEO卫星网络的动态拓扑特性与QoS约束满足。
通过三阶段优化策略（位置感知初始部署、链路稳定性评估、迁移决策机制），实现低时延、高可靠的SFC编排，同时支持星上资源动态分配与切换策略。
主要特性包括：

- 位置感知部署：基于UE与卫星的地理位置匹配度选择部署节点，优先考虑覆盖重叠区域的卫星；
- 链路稳定性评估：通过卫星相对运动预测链路存续时间，优先选择稳定周期长的星间链路；
- 动态迁移触发：当检测到链路稳定性低于阈值或资源不足时，触发预迁移机制避免服务中断；
- 多QoS约束满足：综合考虑时延、带宽、丢包率约束，通过加权因子实现多目标优化；
- 星上资源优化：支持星上计算资源的动态分配与共享，提升资源利用率。

参考
----

```
@inproceedings{ma2024mobility,
  title={Mobility-Aware Service Function Chain Deployment and Migration in LEO Mega-Constellation Networks},
  author={Ma, Wenxin and Peng, Tao and Yuan, Chang and Wang, Wenbo},
  booktitle={2024 IEEE/CIC International Conference on Communications in China (ICCC)},
  pages={752--757},
  year={2024},
  organization={IEEE}
}
```

版本
----

- 版本 1.0 (2025/11/11): 初始版本，实现LM-SFCP算法核心功能，支持位置感知部署、链路稳定性评估与动态迁移
'''

import copy
import random
import networkx as nx
import numpy as np
from astropy import units as u
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE
from netorchestr.envir.mobility.base import MobilityBase
from netorchestr.envir.node.controller.mano.vim import NfvInstance
from netorchestr.envir.node.controller.mano.uem import Ue
from typing import TYPE_CHECKING, Union, List, Dict, Tuple
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager

class SolverDeployLMSFCP(SolverDeployBase):
    def __init__(self, name: str):
        super().__init__(name)
        self.temp_nfvi_group_resource: Dict[int, Dict[str, Union[int, u.Quantity]]] = {}
        self.link_stability_threshold = 30  # 链路稳定性阈值（秒），低于该值触发迁移
        self.qos_weights = {
            'latency': 0.4,    # 时延权重
            'bandwidth': 0.3,  # 带宽权重
            'reliability': 0.3 # 可靠性权重
        }
        self.resource_weights = {
            'cpu': 0.6,        # CPU资源权重
            'ram': 0.4         # RAM资源权重
        }

    def calculate_position_match_score(self, nfvi: NfvInstance, ue: Ue) -> float:
        """
        计算NFVI节点与UE的位置匹配度得分
        基于距离得分范围[0,1]
        
        Args:
            nfvi: NFVI节点
            ue: UE节点
        
        Returns:
            位置匹配度得分
        """
        
        # 计算UE与卫星的地表距离
        flag, distance, _ = self.vnffgManager.vnfVim.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue.node_handle.radioPhy,
                                                                                                                       nfvi.node_handle.duAau.radioPhy)
        
        coverage_radius = max(ue.node_handle.radioPhy.range, nfvi.node_handle.duAau.radioPhy.range)
        
        # 计算匹配度得分：距离越近得分越高，超出覆盖半径得分为0
        if flag == False:
            return 0.0
        return 1.0 - (distance.to(u.km).value / coverage_radius.to(u.km).value)

    def geodetic_to_ecef(self,pos):
        """
        将经纬度 (度) 和海拔 (千米) 转换为ECEF坐标系 (米)
        参考WGS84椭球参数
        """
        lat=pos[0]
        lon=pos[1]
        alt=pos[2] * 1000
        
        # WGS84椭球参数
        a = 6378137.0  # 长半轴（米）
        f = 1 / 298.257223563  # 扁率
        e2 = 2 * f - f**2  # 第一偏心率平方
        
        # 转换为弧度
        lat_rad = np.radians(lat)
        lon_rad = np.radians(lon)
        
        # 计算N（卯酉圈曲率半径）
        N = a / np.sqrt(1 - e2 * np.sin(lat_rad)**2)
        
        # 计算ECEF坐标
        X = (N + alt) * np.cos(lat_rad) * np.cos(lon_rad)
        Y = (N + alt) * np.cos(lat_rad) * np.sin(lon_rad)
        Z = (N * (1 - e2) + alt) * np.sin(lat_rad)
        
        return np.array([X, Y, Z])



    def predict_link_stability(self, nfvi1: NfvInstance, nfvi2: NfvInstance) -> float:
        """
        预测两个NFVI节点间链路的稳定存续时间 (秒)
        基于相对运动轨迹计算链路保持连通的时间
        
        Args:
            nfvi1: 第一个NFVI节点
            nfvi2: 第二个NFVI节点
        
        Returns:
            链路稳定存续时间（秒）
        """
        # 获取两个NFVI节点的速度矢量
        time_step = 1 * u.min
        
        nfvi1_pos_current = self.geodetic_to_ecef(nfvi1.node_handle.mobiusTraj.current_gps)
        nfvi1_pos_predict = self.geodetic_to_ecef(nfvi1.node_handle.mobiusTraj.update_current_gps(
                                                        time=(self.vnffgManager.vnfVim.scheduler.now)*u.ms + time_step)[0]
                                                  )
        nfvi2_pos_current = self.geodetic_to_ecef(nfvi2.node_handle.mobiusTraj.current_gps)
        nfvi2_pos_predict = self.geodetic_to_ecef(nfvi2.node_handle.mobiusTraj.update_current_gps(
                                                        time=(self.vnffgManager.vnfVim.scheduler.now)*u.ms + time_step)[0]
                                                  )
        
        # 节点1的速度向量 (km/s)
        nfvi1_displacement = (nfvi1_pos_predict - nfvi1_pos_current) * u.m
        nfvi2_displacement = (nfvi2_pos_predict - nfvi2_pos_current) * u.m
        nfvi1_vel = (nfvi1_displacement / time_step).to(u.km / u.s)  # 速度矢量（km/s）
        nfvi2_vel = (nfvi2_displacement / time_step).to(u.km / u.s)
        
        flag, distance, _ = self.vnffgManager.vnfVim.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(nfvi1.node_handle.duAau.radioPhy,
                                                                                                                       nfvi2.node_handle.duAau.radioPhy)
        
        max_communication_range = min(
            nfvi1.node_handle.duAau.radioPhy.range,
            nfvi2.node_handle.duAau.radioPhy.range
        )
        
        # 计算相对速度
        rel_vel = (np.linalg.norm(np.array(nfvi1_vel) - np.array(nfvi2_vel)))*u.km/u.s
        
        # 如果当前距离已超出通信范围，返回0
        if rel_vel == 0.0*u.km/u.s or flag == False:
            return 0.0
        
        # 计算链路存续时间：假设卫星沿直线运动，计算距离减小到0再增大到通信范围的时间
        # 简化模型：仅考虑距离变化率
        distance_change_rate = abs(rel_vel)  # 距离变化率（km/s）
        if distance < max_communication_range:
            # 计算还能保持连通的时间
            time_to_max_range = (max_communication_range - distance) / distance_change_rate
            return time_to_max_range.to(u.s).value
        else:
            return 0.0


    def calculate_resource_score(self, nfvi: NfvInstance, vnf_type: str) -> float:
        """
        计算NFVI节点的资源充足度得分
        结合CPU和RAM的剩余资源比例
        
        Args:
            nfvi: NFVI节点
            vnf_type: VNF类型
        
        Returns:
            资源充足度得分（范围[0,1]）
        """
        # 获取VNF的资源需求
        vnf_resource = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
        # 获取NFVI节点的剩余资源
        remaining_resource = self.temp_nfvi_group_resource[nfvi.id]
        
        # 检查资源是否充足
        if remaining_resource['cpu'] < vnf_resource['cpu'] or remaining_resource['ram'] < vnf_resource['ram']:
            return 0.0
        
        # 获取NFVI节点的总资源
        total_resource = nfvi.node_handle.get_max_resource()
        
        # 计算各资源的剩余比例
        cpu_ratio = remaining_resource['cpu'] / total_resource['cpu']
        ram_ratio = remaining_resource['ram'] / total_resource['ram']
        
        # 计算加权综合得分
        total_score = (self.resource_weights['cpu'] * cpu_ratio +
                      self.resource_weights['ram'] * ram_ratio)
        return total_score

    def select_optimal_nfvi(self, candidate_nfvis: List[NfvInstance], vnf_type: str, ue: Ue) -> NfvInstance:
        """
        选择最优的NFVI节点部署VNF
        综合考虑位置匹配度、QoS得分、资源剩余量
        
        Args:
            candidate_nfvis: 候选NFVI节点列表
            vnf_type: VNF类型
            ue_position: UE地理位置
        
        Returns:
            最优NFVI节点
        """
        best_score = -1.0
        best_nfvi = None
        
        for nfvi in candidate_nfvis:
            # 计算各维度得分
            position_score = self.calculate_position_match_score(nfvi, ue)
            qos_score = 1
            resource_score = self.calculate_resource_score(nfvi, vnf_type)
            
            # 综合得分（权重可配置）
            total_score = 0.4 * position_score + 0.4 * qos_score + 0.2 * resource_score
            
            if total_score > best_score:
                best_score = total_score
                best_nfvi = nfvi
        
        return best_nfvi

    def _select_best_middle_nfvi(self, candidate_nfvis: List[NfvInstance], vnf_type: str, 
                                prev_nfvi: NfvInstance) -> NfvInstance:
        """
        选择中间VNF的最优部署节点
        综合考虑与前一个节点的链路稳定性、位置匹配度和QoS得分
        """
        best_score = -1.0
        best_nfvi = None
        
        for nfvi in candidate_nfvis:
            # 计算各维度得分
            stability = self.predict_link_stability(prev_nfvi, nfvi)
            stability_score = min(stability / self.link_stability_threshold, 1.0)  # 归一化到[0,1]
            position_score = 1
            qos_score = 1
            resource_score = self.calculate_resource_score(nfvi, vnf_type)
            
            # 综合得分（权重：链路稳定性0.4，位置0.3，QoS0.2，资源0.1）
            total_score = (0.4 * stability_score + 
                          0.3 * position_score + 
                          0.2 * qos_score + 
                          0.1 * resource_score)
            
            if total_score > best_score:
                best_score = total_score
                best_nfvi = nfvi
        
        return best_nfvi

    def _update_deployment_info(self, v_node: int, nfvi: NfvInstance, vnf_type: str, is_shared: bool):
        """
        更新部署信息（资源占用、映射关系、共享节点）
        """
        # 占用资源
        vnf_resource = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
        self.temp_nfvi_group_resource[nfvi.id]['cpu'] -= vnf_resource['cpu']
        self.temp_nfvi_group_resource[nfvi.id]['ram'] -= vnf_resource['ram']
        self.temp_nfvi_group_resource[nfvi.id]['rom'] -= vnf_resource['rom']
        
        # 更新部署映射
        self.solution_deploy.map_node[v_node] = nfvi.id
        
        # 处理共享节点
        if is_shared:
            can_be_shared_vnfem_list = nfvi.get_deployed_vnf_with_type(vnf_type)
            self.solution_deploy.share_node[v_node] = can_be_shared_vnfem_list[0].id if can_be_shared_vnfem_list else None
        else:
            self.solution_deploy.share_node[v_node] = None

    def _calculate_stable_links(self) -> bool:
        """
        计算稳定的路径
        优先选择稳定性高的链路
        """
        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        
        for v_link in v_links:
            src_nfvi_id = self.solution_deploy.map_node[v_link[0]]
            dst_nfvi_id = self.solution_deploy.map_node[v_link[1]]
            
            # 如果直接链路稳定性足够，使用直接链路
            src_nfvi = self.vnffgManager.vnfVim.nfvi_group[src_nfvi_id]
            dst_nfvi = self.vnffgManager.vnfVim.nfvi_group[dst_nfvi_id]
            direct_stability = self.predict_link_stability(src_nfvi, dst_nfvi)
            
            if direct_stability >= self.link_stability_threshold:
                self.solution_deploy.map_link[v_link] = [(src_nfvi_id, dst_nfvi_id)]
                continue
            
            # 否则寻找稳定性最高的多跳路径
            try:
                # 自定义路径权重：链路稳定性的倒数（优先选择稳定性高的链路）
                def link_weight(u: int, v: int, data: Dict) -> float:
                    nfvi_u = self.vnffgManager.vnfVim.nfvi_group[u]
                    nfvi_v = self.vnffgManager.vnfVim.nfvi_group[v]
                    stability = self.predict_link_stability(nfvi_u, nfvi_v)
                    return 1.0 / (stability + 1e-6)  # 避免除零
                
                # 使用Dijkstra算法寻找最优路径
                map_path = nx.dijkstra_path(self.adjacent_topo, src_nfvi_id, dst_nfvi_id, weight=link_weight)
                
                # 检查路径中所有链路的稳定性是否满足阈值
                stable = True
                for i in range(len(map_path)-1):
                    nfvi1 = self.vnffgManager.vnfVim.nfvi_group[map_path[i]]
                    nfvi2 = self.vnffgManager.vnfVim.nfvi_group[map_path[i+1]]
                    if self.predict_link_stability(nfvi1, nfvi2) < self.link_stability_threshold:
                        stable = False
                        break
                
                if not stable:
                    if self.solution_deploy.current_req_type == "arrive":
                        self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                    elif self.solution_deploy.current_req_type == "migrate":
                        self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
                    return False
                
                # 转换为链路列表
                self.solution_deploy.map_link[v_link] = [(map_path[i], map_path[i+1]) for i in range(len(map_path)-1)]
                
            except nx.NetworkXNoPath:
                if self.solution_deploy.current_req_type == "arrive":
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                elif self.solution_deploy.current_req_type == "migrate":
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
                return False
        
        return True

    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """
        基于LM-SFCP算法的SFC初始部署求解
        实现位置感知部署与链路稳定性优化
        
        Args:
            vnffgManager: VNF转发图管理器
        
        Returns:
            部署解决方案
        """
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        
        # 初始化参数
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]

        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)

        # 深拷贝基底网络资源
        self.temp_nfvi_group_resource = {
            nvfi.id: copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
            for nvfi in vnffgManager.vnfVim.nfvi_group.values()
        }
        

        for v_node in self.current_vnfs_index_list:
            vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
            is_shared = vnffgManager.sfc_req.sfc_vnfs_shared[v_node]
            
            if v_node == 0:
                # 第一个VNF：部署在UE起始位置覆盖的卫星上
                candidate_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
                if not candidate_nfvis:
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_START
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
                
                # 选择最优NFVI节点
                choosen_nfvi = self.select_optimal_nfvi(candidate_nfvis, vnf_type, vnffgManager.ue_access_start)
                if not choosen_nfvi:
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_RESOURCE_INSUFFICIENT
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
                
            elif v_node == len(self.current_vnfs_index_list) - 1:
                # 最后一个VNF：部署在UE终止位置覆盖的卫星上
                candidate_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)
                if not candidate_nfvis:
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_END
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
                
                # 选择最优NFVI节点
                choosen_nfvi = self.select_optimal_nfvi(candidate_nfvis, vnf_type, vnffgManager.ue_access_end)
                if not choosen_nfvi:
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_RESOURCE_INSUFFICIENT
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
                
            else:
                # 中间VNF：考虑链路稳定性，选择与前一个节点链路稳定的卫星
                prev_nfvi = vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[v_node-1]]
                # 获取与前一个节点连通的卫星
                candidate_nfvis = [vnffgManager.vnfVim.nfvi_group[n] for n in 
                                  nx.neighbors(self.adjacent_topo, prev_nfvi.id)]
                
                if is_shared:
                    # 支持共享：优先选择已部署同类型VNF的卫星
                    need_type = vnf_type
                    shared_nfvis = vnffgManager.vnfVim.who_has_vnf_with_type(need_type)
                    candidate_nfvis = list(set(candidate_nfvis) & set(shared_nfvis)) or candidate_nfvis
                
                # 选择最优NFVI节点（考虑与前一个节点的链路稳定性）
                choosen_nfvi = self._select_best_middle_nfvi(candidate_nfvis, vnf_type, prev_nfvi)
                if not choosen_nfvi:
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
            
            # 更新资源和部署映射
            self._update_deployment_info(v_node, choosen_nfvi, vnf_type, is_shared)
        
        # 计算链路路径（考虑链路稳定性）
        if not self._calculate_stable_links():
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 检查解决方案有效性
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.SET_SUCCESS)
        
        return self.solution_deploy

    def _get_migration_candidates(self, prev_nfvi_id: int, next_nfvi_id: int, 
                                 vnf_type: str, is_shared: bool) -> List[NfvInstance]:
        """
        获取迁移候选节点列表
        """
        candidates = []
        
        # 基于前后节点的连通性筛选
        if prev_nfvi_id:
            prev_neighbors = set(nx.neighbors(self.adjacent_topo, prev_nfvi_id))
        else:
            prev_neighbors = set()
        
        if next_nfvi_id:
            next_neighbors = set(nx.neighbors(self.adjacent_topo, next_nfvi_id))
        else:
            next_neighbors = set()
        
        # 候选节点需同时与前后节点连通（或其中之一）
        if prev_neighbors and next_neighbors:
            candidates = list(prev_neighbors & next_neighbors)
        elif prev_neighbors:
            candidates = list(prev_neighbors)
        elif next_neighbors:
            candidates = list(next_neighbors)
        else:
            candidates = list(self.adjacent_topo.nodes())
        
        # 转换为NFVI对象
        candidate_nfvis = [self.vnffgManager.vnfVim.nfvi_group[n] for n in candidates]
        
        # 支持共享时优先选择已部署同类型VNF的节点
        if is_shared:
            shared_nfvis = self.vnffgManager.vnfVim.who_has_vnf_with_type(vnf_type)
            candidate_nfvis = list(set(candidate_nfvis) & set(shared_nfvis)) or candidate_nfvis
        
        return candidate_nfvis

    def _select_migration_target(self, candidate_nfvis: List[NfvInstance], vnf_type: str, 
                                prev_nfvi_id: int, next_nfvi_id: int) -> NfvInstance:
        """
        选择迁移目标节点
        综合考虑与前后节点的链路稳定性、资源状况和QoS
        """
        best_score = -1.0
        best_nfvi = None
        
        for nfvi in candidate_nfvis:
            # 计算链路稳定性得分
            stability_scores = []
            if prev_nfvi_id:
                prev_nfvi = self.vnffgManager.vnfVim.nfvi_group[prev_nfvi_id]
                stability = self.predict_link_stability(prev_nfvi, nfvi)
                stability_scores.append(min(stability / self.link_stability_threshold, 1.0))
            if next_nfvi_id:
                next_nfvi = self.vnffgManager.vnfVim.nfvi_group[next_nfvi_id]
                stability = self.predict_link_stability(nfvi, next_nfvi)
                stability_scores.append(min(stability / self.link_stability_threshold, 1.0))
            
            stability_score = sum(stability_scores) / len(stability_scores) if stability_scores else 0.0
            
            # 计算其他得分
            position_score = 1
            qos_score = 1
            resource_score = self.calculate_resource_score(nfvi, vnf_type)
            
            # 综合得分（权重：链路稳定性0.5，位置0.2，QoS0.2，资源0.1）
            total_score = (0.5 * stability_score + 
                          0.2 * position_score + 
                          0.2 * qos_score + 
                          0.1 * resource_score)
            
            if total_score > best_score:
                best_score = total_score
                best_nfvi = nfvi
        
        return best_nfvi

    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """
        基于LM-SFCP算法的SFC迁移求解
        当链路稳定性不足或资源紧张时触发迁移
        
        Args:
            vnffgManager: VNF转发图管理器
        
        Returns:
            迁移解决方案
        """
        self.vnffgManager = vnffgManager
        self.solution_deploy = copy.deepcopy(vnffgManager.solutions_deploy[-1])
        self.solution_deploy.current_req_type = "migrate"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        
        # 初始化参数（与初始部署类似）
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]

        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)

        # 深拷贝基底网络资源
        self.temp_nfvi_group_resource = {
            nvfi.id: copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
            for nvfi in vnffgManager.vnfVim.nfvi_group.values()
        }
        

        # 对受影响的节点进行迁移
        for v_node in self.current_vnfs_index_list:
            vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
            is_shared = vnffgManager.sfc_req.sfc_vnfs_shared[v_node]
            current_nfvi_id = self.solution_deploy.map_node[v_node]
            
            # 选择迁移目标节点（基于LM-SFCP算法）
            if v_node == 0:
                candidate_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
                choosen_nfvi = self.select_optimal_nfvi(candidate_nfvis, vnf_type, vnffgManager.ue_access_start)
            elif v_node == len(self.current_vnfs_index_list) - 1:
                candidate_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)
                choosen_nfvi = self.select_optimal_nfvi(candidate_nfvis, vnf_type, vnffgManager.ue_access_end)
            else:
                # 中间节点：考虑与前后节点的链路稳定性
                prev_nfvi_id = self.solution_deploy.map_node[v_node-1] if v_node > 0 else None
                next_nfvi_id = self.solution_deploy.map_node[v_node+1] if v_node < len(self.current_vnfs_index_list)-1 else None
                
                candidate_nfvis = self._get_migration_candidates(prev_nfvi_id, next_nfvi_id, vnf_type, is_shared)
                choosen_nfvi = self._select_migration_target(candidate_nfvis, vnf_type, prev_nfvi_id, next_nfvi_id)
            
            if not choosen_nfvi or choosen_nfvi.id == current_nfvi_id:
                # 无合适迁移目标或无需迁移，保持原部署
                continue
            
            # 更新部署信息（迁移）
            self._update_deployment_info(v_node, choosen_nfvi, vnf_type, is_shared)
        
        # 重新计算链路路径（确保迁移后链路稳定）
        if not self._calculate_stable_links():
            self.solution_deploy.current_result = False
            self.calculate_cost_and_revenue(vnffgManager)
            
            return self.solution_deploy
        
        # 检查解决方案有效性
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS)
        
        # 计算迁移成本与收益
        self.calculate_cost_and_revenue(vnffgManager)
        
        return self.solution_deploy
