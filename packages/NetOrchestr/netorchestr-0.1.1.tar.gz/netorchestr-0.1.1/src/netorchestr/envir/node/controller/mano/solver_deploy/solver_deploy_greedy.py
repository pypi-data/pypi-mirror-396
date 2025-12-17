#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_greedy.py
=======================

.. module:: solver_deploy_greedy
  :platform: Windows
  :synopsis: 基于贪心策略的 SFC 编排求解器模块, 支持虚拟网络功能 (VNF) 共享部署，实现 VNF 向物理设施节点 (NFVI) 的高效嵌入与迁移

.. moduleauthor:: WangXi

简介
----

该模块实现了贪心算法驱动的服务功能链 (SFC) 部署与迁移求解逻辑, 核心聚焦 VNF 共享能力与物理节点资源利用率优化。
通过优先选择剩余资源充足的 NFVI 节点，结合 VNF 共享状态判断，实现 SFC 上微服务实例的合理嵌入，同时支持部署失败的多场景异常处理。
它提供了以下特性：

- 支持 VNF 共享部署：对标记为可共享的 VNF, 优先选择已部署同类型 VNF 的 NFVI 节点，减少重复部署的资源消耗；
- 贪心资源选择策略：通过 who_has_most_resource 方法筛选剩余 CPU 资源最多的 NFVI 节点，提升资源利用率；
- 完整的部署与迁移流程：分别实现 SFC 接入时的初始部署 (solve_embedding) 与运行时的迁移部署 (solve_migration)
- 严格的接入与路由约束：起始 / 终止 VNF 限定部署在 UE 端点可接入的 NFVI 上，中间链路通过 Dijkstra 算法保证路由可达；
- 完善的异常处理：覆盖 UE 接入失败、路由不可达等场景，返回明确的部署结果描述与状态标记。

版本
----

- 版本 1.0 (2025/11/11): 初始版本，集成 VNF 共享部署、贪心资源选择、部署与迁移核心功能

'''

import copy
import random
import networkx as nx
import numpy as np

from astropy import units as u
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE
from netorchestr.envir.node.controller.mano.vim import NfvInstance

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager
    
class SolverDeploySharedGreedy(SolverDeployBase):
    def __init__(self, name:str):
        super().__init__(name)
        
        self.temp_nfvi_group_resouce = {}

    def who_has_most_resource(self, nfvi_list:list[NfvInstance], resource_type:str) -> NfvInstance:
        """获取列表中 NFVI 节点中拥有最多剩余资源的 NFVI 节点 \
        
        数据来源于 self.temp_nfvi_group_resouce

        Args:
            list_nfvi (list[NfvInstance]): 列表中 NFVI 节点
            resource_type (str): 资源类型

        Returns:
            NfvInstance: 列表中 NFVI 节点中拥有最多资源的 NFVI 节点
        """
        max_resource = 0
        max_nfvi = random.choice(nfvi_list)
        for nfvi in nfvi_list:
            nfvi_resource = self.temp_nfvi_group_resouce[nfvi.id].get(resource_type)
            if nfvi_resource > max_resource:
                max_resource = nfvi_resource
                max_nfvi = nfvi
                
        return max_nfvi

    def solve_embedding(self,vnffgManager:"VnffgManager") -> SolutionDeploy:
        """
        部署方案

        Args:
            vnffgManager (VnffgManager): _description_

        Returns:
            SolutionDeploy: _description_
            
        Note:
            部署最终决策仅依赖于一个映射关系, 而不对实际的网络设置进行操作, 
            
            在部署开始就应该深拷贝基底网络资源, 便于进行资源的暂时性修改辅助决策过程. 
        """
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

        # 深拷贝基底网络资源, 便于进行资源的暂时性修改辅助决策过程
        self.temp_nfvi_group_resouce:dict[int,dict[str,Union[int,u.Quantity]]] = \
            {nvfi.id : copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
             for nvfi in vnffgManager.vnfVim.nfvi_group.values()}
        
        for v_node in self.current_vnfs_index_list:
            if v_node == 0:
                # 第一个 VNF 部署在 UE 起始端点可接入的 NFVI 上
                can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
                if can_access_nfvi_list == []: # 起始用户端点没有 NFVI 可接入
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_START
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
                                
                choosen_nfvi_to_vnf = self.who_has_most_resource(can_access_nfvi_list, 'cpu')
                choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']
                
                self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_vnfem_list = choosen_nfvi_to_vnf.get_deployed_vnf_with_type(need_type)
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
                
                choosen_nfvi_to_vnf = self.who_has_most_resource(can_access_nfvi_list, 'cpu')
                choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']
                
                self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_vnfem_list = choosen_nfvi_to_vnf.get_deployed_vnf_with_type(need_type)
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
                        
                        choosen_nfvi_to_vnf = self.who_has_most_resource(nfvi_list_can_be_routed, 'cpu')
                        choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                        self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']

                        self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
                        self.solution_deploy.share_node[v_node] = None
                    else:
                        # 该 VNF 类型已经部署在某些 NFVI 上，则随机选择其中一个 NFVI 部署
                        choosen_nfvi_to_vnf = self.who_has_most_resource(can_be_shared_nfvi_list, 'cpu')
                        choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                        self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']
                        
                        self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
                        can_be_shared_vnfem_list = choosen_nfvi_to_vnf.get_deployed_vnf_with_type(need_type)                   
                        if len(can_be_shared_vnfem_list) == 0:
                            self.solution_deploy.share_node[v_node] = None
                        else:
                            self.solution_deploy.share_node[v_node] = can_be_shared_vnfem_list[0].id
                else:
                    # 该 VNF 不支持被共享使用，则随机部署在可被路由到的 NFVI 上
                    nfvi_start_access = vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
                    nfvi_list_can_be_routed = vnffgManager.vnfVim.who_can_route_to_nfvi(nfvi_start_access, self.adjacent_topo)
                    
                    choosen_nfvi_to_vnf = self.who_has_most_resource(nfvi_list_can_be_routed, 'cpu')
                    choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']
                    
                    self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
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
        
        
        # region 准备算法所需数据 ---------------------------------------------
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

        # 深拷贝基底网络资源, 便于进行资源的暂时性修改辅助决策过程
        self.temp_nfvi_group_resouce:dict[int,dict[str,Union[int,u.Quantity]]] = \
            {nvfi.id : copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
             for nvfi in vnffgManager.vnfVim.nfvi_group.values()}
                
        for v_node in self.current_vnfs_index_list:
            if v_node == 0:
                # 第一个 VNF 部署在 UE 起始端点可接入的 NFVI 上
                can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
                if can_access_nfvi_list == []: # 起始用户端点没有 NFVI 可接入
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_UE_ACCESS_START
                    self.solution_deploy.current_result = False
                    return self.solution_deploy
                
                choosen_nfvi_to_vnf = self.who_has_most_resource(can_access_nfvi_list, 'cpu')
                choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']
                
                self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_vnfem_list = choosen_nfvi_to_vnf.get_deployed_vnf_with_type(need_type)
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

                choosen_nfvi_to_vnf = self.who_has_most_resource(can_access_nfvi_list, 'cpu')
                choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']
                
                self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
                # 检查该 VNF 是否支持被共享使用
                if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                    need_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    can_be_shared_vnfem_list = choosen_nfvi_to_vnf.get_deployed_vnf_with_type(need_type)
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
                        
                        choosen_nfvi_to_vnf = self.who_has_most_resource(nfvi_list_can_be_routed, 'cpu')
                        choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                        self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']
                        
                        self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
                        self.solution_deploy.share_node[v_node] = None
                    else:
                        # 该 VNF 类型已经部署在某些 NFVI 上，则随机选择其中一个 NFVI 部署
                        choosen_nfvi_to_vnf = self.who_has_most_resource(can_be_shared_nfvi_list, 'cpu')
                        choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                        self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']
                        
                        self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
                        can_be_shared_vnfem_list = choosen_nfvi_to_vnf.get_deployed_vnf_with_type(need_type)
                        if len(can_be_shared_vnfem_list) == 0:
                            self.solution_deploy.share_node[v_node] = None
                        else:
                            self.solution_deploy.share_node[v_node] = can_be_shared_vnfem_list[0].id
                else:
                    # 该 VNF 不支持被共享使用，则随机部署在 NFVI 上
                    nfvi_start_access = vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
                    nfvi_list_can_be_routed = vnffgManager.vnfVim.who_can_route_to_nfvi(nfvi_start_access, self.adjacent_topo)
                    
                    choosen_nfvi_to_vnf = self.who_has_most_resource(nfvi_list_can_be_routed, 'cpu')
                    choosen_nfvi_vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                    self.temp_nfvi_group_resouce[choosen_nfvi_to_vnf.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[choosen_nfvi_vnf_type_need].resource_limit['cpu']
                    
                    self.solution_deploy.map_node[v_node] = choosen_nfvi_to_vnf.id
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

