#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_random.py
=======================

.. module:: solver_deploy_random
  :platform: Windows
  :synopsis: 基于随机策略的 SFC 编排求解器模块, 支持虚拟网络功能 (VNF) 共享部署, 实现 VNF 向物理设施节点 (NFVI) 的快速嵌入与迁移
  
.. moduleauthor:: WangXi

简介
----

该模块采用随机部署策略, 为服务功能链 (SFC) 提供轻量、高效的 VNF 嵌入与迁移方案，核心支持 VNF 共享部署特性，同时满足 UE 接入约束与路由可达性要求。
通过随机选择符合条件的 NFVI 节点，降低部署决策的计算复杂度，适用于对实时性要求较高或作为基准对比的场景。
它提供了以下特性：

- 支持 VNF 共享部署：对标记为可共享的 VNF, 优先随机选择已部署同类型 VNF 的 NFVI 节点，减少资源重复消耗;
- 随机部署核心策略：起始 / 终止 VNF 从 UE 端点可接入的 NFVI 中随机选择，中间 VNF 从路由可达的 NFVI 中随机选择，决策高效;
- 完整的部署与迁移流程：分别实现 SFC 接入时的初始部署 (solve_embedding) 与运行时的迁移部署 (solve_migration);
- 严格的约束校验：保障 UE 接入可达、VNF 部署路由连通，通过 Dijkstra 算法获取节点间链路，确保 SFC 链路完整性;
- 完善的异常处理：覆盖 UE 接入失败、路由不可达等场景，返回明确的部署结果描述与状态标记;
- 轻量低开销：无复杂优化计算，部署决策速度快，适用于大规模网络或实时部署场景，也可作为其他优化算法的性能基准. 

版本
----

- 版本 1.0 (2025/11/11): 初始版本，集成 VNF 共享部署、随机节点选择、部署与迁移核心功能

'''

import random
import networkx as nx
import numpy as np

from astropy import units as u
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager
    

class SolverDeploySharedRandom(SolverDeployBase):
    def __init__(self, name:str):
        super().__init__(name)

    def solve_embedding(self,vnffgManager:"VnffgManager") -> SolutionDeploy:
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        self.current_nfvi_index_list = list(self.nfvOrchestrator.vnfVim.nfvi_group.keys())
                
        # algorithm begin ---------------------------------------------
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
        
        for v_node in self.current_vnfs_index_list:
            if v_node == 0:
                # 第一个 VNF 部署在 UE 起始端点可接入的 NFVI 上
                can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
                if can_access_nfvi_list == []: # 起始用户端点没有 NFVI 可接入
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_START
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
                    
                choosen_nfvi_to_ue_start = random.choice(can_access_nfvi_list)
                self.solution_deploy.map_node[v_node] = choosen_nfvi_to_ue_start.id
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_vnfem_list = choosen_nfvi_to_ue_start.get_deployed_vnf_with_type(need_type)
                    if len(can_be_shared_vnfem_list) == 0:
                        self.solution_deploy.share_node[v_node] = None
                    else:
                        self.solution_deploy.share_node[v_node] = can_be_shared_vnfem_list[0].id
                
            elif v_node == (len(self.current_vnfs_index_list)-1):
                # 最后一个 VNF 部署在 UE 终止端点可接入的 NFVI 上
                can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)
                if can_access_nfvi_list == []: # 终止用户端点没有 NFVI 可接入
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_END
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
                
                choosen_nfvi_to_ue_end = random.choice(can_access_nfvi_list)
                self.solution_deploy.map_node[v_node] = choosen_nfvi_to_ue_end.id
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_vnfem_list = choosen_nfvi_to_ue_end.get_deployed_vnf_with_type(need_type)
                    if len(can_be_shared_vnfem_list) == 0:
                        self.solution_deploy.share_node[v_node] = None
                    else:
                        self.solution_deploy.share_node[v_node] = can_be_shared_vnfem_list[0].id
            else:
                # 其他 VNF 随机部署在 NFVI 上
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    # 该 VNF 支持被共享使用，则可以挑选已经部署了的 VNF 进行共享，选择其 NFVI 部署
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_nfvi_list = vnffgManager.vnfVim.who_has_vnf_with_type(need_type)
                    if len(can_be_shared_nfvi_list) == 0:
                        # 该 VNF 类型没有部署在任何 NFVI 上，则随机部署在可被路由到的 NFVI 上
                        nfvi_start_access = vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
                        nfvi_list_can_be_routed = vnffgManager.vnfVim.who_can_route_to_nfvi(nfvi_start_access,self.adjacent_topo)
                        nfvi_id_list_can_be_routed = [nfvi.id for nfvi in nfvi_list_can_be_routed]

                        self.solution_deploy.map_node[v_node] = random.sample(nfvi_id_list_can_be_routed, 1)[0]
                        self.solution_deploy.share_node[v_node] = None
                    else:
                        # 该 VNF 类型已经部署在某些 NFVI 上，则随机选择其中一个 NFVI 部署
                        can_be_shared_nfvi = random.sample(can_be_shared_nfvi_list, 1)[0]
                        self.solution_deploy.map_node[v_node] = can_be_shared_nfvi.id
                        can_be_shared_vnfem_list = can_be_shared_nfvi.get_deployed_vnf_with_type(need_type)                   
                        if len(can_be_shared_vnfem_list) == 0:
                            self.solution_deploy.share_node[v_node] = None
                        else:
                            self.solution_deploy.share_node[v_node] = can_be_shared_vnfem_list[0].id
                            
                else:
                    # 该 VNF 不支持被共享使用，则随机部署在可被路由到的 NFVI 上
                    nfvi_start_access = vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
                    nfvi_list_can_be_routed = vnffgManager.vnfVim.who_can_route_to_nfvi(nfvi_start_access, self.adjacent_topo)
                    nfvi_id_list_can_be_routed = [nfvi.id for nfvi in nfvi_list_can_be_routed]
                    
                    self.solution_deploy.map_node[v_node] = random.sample(nfvi_id_list_can_be_routed, 1)[0]
                    self.solution_deploy.share_node[v_node] = None
                    
        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.adjacent_topo, self.solution_deploy.map_node[v_link[0]], self.solution_deploy.map_node[v_link[1]])
            except:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            if len(map_path) == 1:
                self.solution_deploy.map_link[v_link] = [(map_path[0], map_path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]
        # algorithm end ---------------------------------------------

        self.solution_deploy.current_description = self.check_solution(vnffgManager)

        if self.solution_deploy.current_description != SOLUTION_DEPLOY_TYPE.SET_SUCCESS:
            self.solution_deploy.current_result = False
        else:
            self.solution_deploy.current_result = True
        return self.solution_deploy
        
    def solve_migration(self,vnffgManager:"VnffgManager") -> SolutionDeploy:
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "migrate"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        self.current_nfvi_index_list = list(vnffgManager.vnfVim.nfvi_group.keys())
        
        # algorithm begin ---------------------------------------------
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
        
        for v_node in self.current_vnfs_index_list:
            if v_node == 0:
                # 第一个 VNF 部署在 UE 起始端点可接入的 NFVI 上
                can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
                if can_access_nfvi_list == []: # 起始用户端点没有 NFVI 可接入
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_UE_ACCESS_START
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
                
                choosen_nfvi_to_ue_start = random.choice(can_access_nfvi_list)
                self.solution_deploy.map_node[v_node] = choosen_nfvi_to_ue_start.id
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_vnfem_list = choosen_nfvi_to_ue_start.get_deployed_vnf_with_type(need_type)
                    if len(can_be_shared_vnfem_list) == 0:
                        self.solution_deploy.share_node[v_node] = None
                    else:
                        self.solution_deploy.share_node[v_node] = can_be_shared_vnfem_list[0].id
                
            elif v_node == (len(self.current_vnfs_index_list)-1):
                # 最后一个 VNF 部署在 UE 终止端点可接入的 NFVI 上
                can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)
                if can_access_nfvi_list == []: # 终止用户端点没有 NFVI 可接入
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_UE_ACCESS_END
                    self.solution_deploy.current_result = False
                    return self.solution_deploy

                choosen_nfvi_to_ue_end = random.choice(can_access_nfvi_list)
                self.solution_deploy.map_node[v_node] = choosen_nfvi_to_ue_end.id
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_vnfem_list = choosen_nfvi_to_ue_end.get_deployed_vnf_with_type(need_type)
                    if len(can_be_shared_vnfem_list) == 0:
                        self.solution_deploy.share_node[v_node] = None
                    else:
                        self.solution_deploy.share_node[v_node] = can_be_shared_vnfem_list[0].id
            else:
                # 其他 VNF 随机部署在 NFVI 上
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    # 该 VNF 支持被共享使用，则可以挑选已经部署了的 VNF 进行共享，选择其 NFVI 部署
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_nfvi_list = vnffgManager.vnfVim.who_has_vnf_with_type(need_type)
                    if len(can_be_shared_nfvi_list) == 0:
                        # 该 VNF 类型没有部署在任何 NFVI 上，则随机部署在 NFVI 上
                        nfvi_start_access = vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
                        nfvi_list_can_be_routed = vnffgManager.vnfVim.who_can_route_to_nfvi(nfvi_start_access, self.adjacent_topo)
                        nfvi_id_list_can_be_routed = [nfvi.id for nfvi in nfvi_list_can_be_routed]
                        
                        self.solution_deploy.map_node[v_node] = random.sample(nfvi_id_list_can_be_routed, 1)[0]
                        self.solution_deploy.share_node[v_node] = None
                    else:
                        # 该 VNF 类型已经部署在某些 NFVI 上，则随机选择其中一个 NFVI 部署
                        can_be_shared_nfvi = random.sample(can_be_shared_nfvi_list, 1)[0]
                        self.solution_deploy.map_node[v_node] = can_be_shared_nfvi.id
                        can_be_shared_vnfem_list = can_be_shared_nfvi.get_deployed_vnf_with_type(need_type)
                        if len(can_be_shared_vnfem_list) == 0:
                            self.solution_deploy.share_node[v_node] = None
                        else:
                            self.solution_deploy.share_node[v_node] = can_be_shared_vnfem_list[0].id
                else:
                    # 该 VNF 不支持被共享使用，则随机部署在 NFVI 上
                    nfvi_start_access = vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
                    nfvi_list_can_be_routed = vnffgManager.vnfVim.who_can_route_to_nfvi(nfvi_start_access, self.adjacent_topo)
                    nfvi_id_list_can_be_routed = [nfvi.id for nfvi in nfvi_list_can_be_routed]
                    
                    self.solution_deploy.map_node[v_node] = random.sample(nfvi_id_list_can_be_routed, 1)[0]
                    self.solution_deploy.share_node[v_node] = None
                    
        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.adjacent_topo, self.solution_deploy.map_node[v_link[0]], self.solution_deploy.map_node[v_link[1]])
            except:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            if len(map_path) == 1:
                self.solution_deploy.map_link[v_link] = [(map_path[0], map_path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]
           
        # algorithm end ---------------------------------------------

        self.solution_deploy.current_description = self.check_solution(vnffgManager)

        if self.solution_deploy.current_description != SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS:
            self.solution_deploy.current_result = False
        else:
            self.solution_deploy.current_result = True

        self.calculate_cost_and_revenue(vnffgManager)
        
        return self.solution_deploy

