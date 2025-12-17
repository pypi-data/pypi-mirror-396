#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_pso.py
====================

.. module:: solver_deploy_pso
  :platform: Windows
  :synopsis: 基于粒子群优化 (PSO) 算法的 SFC 编排求解器模块, 支持虚拟网络功能 (VNF) 共享部署, 实现 VNF 向物理设施节点 (NFVI) 的优化嵌入与迁移

.. moduleauthor:: WangXi

简介
----

该模块融合粒子群优化 (PSO) 算法与贪心策略, 实现服务功能链 (SFC) 的高效部署与迁移, 核心目标是在支持 VNF 共享的前提下, 优化部署的网络时延与资源利用率.
通过 PSO 算法搜索最优中间 VNF 部署位置，结合贪心策略选择资源充足的 NFVI 节点，同时保障部署的路由可达性与 QoS 约束。它提供了以下特性：

- 支持 VNF 共享部署：对标记为可共享的 VNF, 优先匹配已部署同类型 VNF 的 NFVI 节点，降低资源冗余;
- PSO 优化中间 VNF 部署：起始与终止 VNF 按 UE 接入约束部署，中间 VNF 通过 PSO 算法搜索最优 NFVI 节点，最小化时延偏差;
- 贪心资源筛选基础：通过 who_has_most_resource 方法优先选择剩余 CPU 资源充足的 NFVI 节点，提升资源利用效率;
- 完整的部署与迁移流程：分别实现 SFC 接入时的初始部署 (solve_embedding) 与运行时的迁移部署 (solve_migration);
- 严格的约束与异常处理：保障 UE 接入可达、路由连通性，覆盖接入失败、路由不可达等场景，返回明确的部署结果与描述;
- 时延优化目标：适应度函数以 “实际时延与 QoS 时延约束的偏差” 为优化目标，提升部署方案的 QoS 满足度.

版本
----

- 版本 1.0 (2025/11/11): 初始版本，集成 PSO 优化算法、VNF 共享部署、贪心资源选择、部署与迁移核心功能

'''


import copy
import random
import networkx as nx
import numpy as np

from astropy import units as u
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE
from netorchestr.envir.node.controller.mano.vim import NfvInstance
from sko.PSO import PSO

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager
    
class SolverDeploySharedPso(SolverDeployBase):
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
            if nfvi_resource >= max_resource:
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

        # region 算法做出部署决策 ---------------------------------------------
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
                # 其他 VNF 的部署稍后处理
                continue
        
        nfvi_start_access = vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
        self.nfvi_list_can_be_routed = vnffgManager.vnfVim.who_can_route_to_nfvi(nfvi_start_access,self.adjacent_topo)
        self.nfvi_list_can_be_routed_map = {i:nfvi.id for i,nfvi in enumerate(self.nfvi_list_can_be_routed)}
        
        self.pso_x_dim_1 = len(self.current_vnfs_index_list)-2
        self.pso_x_dim_2 = len(self.nfvi_list_can_be_routed)
        self.pso_x_dim = self.pso_x_dim_1*self.pso_x_dim_2
        pso = PSO(
    	    func=self.fitness, 
    	    dim=self.pso_x_dim,
            pop=10, 
    	    max_iter=10, 
    	    lb=[0]*self.pso_x_dim, 
    	    ub=[1]*self.pso_x_dim, 
    	    w=0.8,
    	    c1=0.5, 
    	    c2=0.5)
        pso.run()
        
        x = np.array(pso.gbest_x)
        x = x.reshape((self.pso_x_dim_1,self.pso_x_dim_2))
        for v_node in self.current_vnfs_index_list:
            if v_node != 0 and v_node != (len(self.current_vnfs_index_list)-1):
                max_index = np.where(x[v_node-1,:]==np.max(x[v_node-1,:]))[0][0]
                self.solution_deploy.map_node[v_node] = self.nfvi_list_can_be_routed_map[max_index]
        self.solution_deploy.map_node = dict(sorted(self.solution_deploy.map_node.items()))

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
           
        # region 检查算法决策结果 ---------------------------------------------

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
        
        self.temp_nfvi_group_resouce:dict[int,dict[str,Union[int,u.Quantity]]] = \
            {nvfi.id : copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
             for nvfi in vnffgManager.vnfVim.nfvi_group.values()}
        """深拷贝基底网络资源, 便于进行资源的暂时性修改辅助决策过程"""
        
        # region 算法做出部署决策 ---------------------------------------------
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
                # 其他 VNF 的部署稍后处理
                continue
        
        nfvi_start_access = vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
        self.nfvi_list_can_be_routed = vnffgManager.vnfVim.who_can_route_to_nfvi(nfvi_start_access,self.adjacent_topo)
        self.nfvi_list_can_be_routed_map = {i:nfvi.id for i,nfvi in enumerate(self.nfvi_list_can_be_routed)}
        
        self.pso_x_dim_1 = len(self.current_vnfs_index_list)-2
        self.pso_x_dim_2 = len(self.nfvi_list_can_be_routed)
        self.pso_x_dim = self.pso_x_dim_1*self.pso_x_dim_2
        pso = PSO(
    	    func=self.fitness, 
    	    dim=self.pso_x_dim,
            pop=10, 
    	    max_iter=10, 
    	    lb=[0]*self.pso_x_dim, 
    	    ub=[1]*self.pso_x_dim, 
    	    w=0.8,
    	    c1=0.5, 
    	    c2=0.5)
        pso.run()
        
        x = np.array(pso.gbest_x)
        x = x.reshape((self.pso_x_dim_1,self.pso_x_dim_2))
        for v_node in self.current_vnfs_index_list:
            if v_node != 0 and v_node != (len(self.current_vnfs_index_list)-1):
                max_index = np.where(x[v_node-1,:]==np.max(x[v_node-1,:]))[0][0]
                self.solution_deploy.map_node[v_node] = self.nfvi_list_can_be_routed_map[max_index]
        self.solution_deploy.map_node = dict(sorted(self.solution_deploy.map_node.items()))
        
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
           
        # 检查算法决策结果 ---------------------------------------------------
        self.solution_deploy.current_description = self.check_solution(vnffgManager)

        if self.solution_deploy.current_description != SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS:
            self.solution_deploy.current_result = False
        else:
            self.solution_deploy.current_result = True

        self.calculate_cost_and_revenue(vnffgManager)

        return self.solution_deploy


    def fitness(self,*Args):
        x = np.array(Args)
        x = x.reshape((self.pso_x_dim_1,self.pso_x_dim_2))
        for v_node in self.current_vnfs_index_list:
            if v_node != 0 and v_node != (len(self.current_vnfs_index_list)-1):
                max_index = np.where(x[v_node-1,:]==np.max(x[v_node-1,:]))[0][0]
                self.solution_deploy.map_node[v_node] = self.nfvi_list_can_be_routed_map[max_index]
        self.solution_deploy.map_node = dict(sorted(self.solution_deploy.map_node.items()))

        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.adjacent_topo, self.solution_deploy.map_node[v_link[0]], self.solution_deploy.map_node[v_link[1]])
            except:
                return float("inf")
            
            if len(map_path) == 1:
                self.solution_deploy.map_link[v_link] = [(map_path[0], map_path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]

        if self.check_solution(self.vnffgManager) not in (SOLUTION_DEPLOY_TYPE.SET_SUCCESS,
                                                          SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS,
                                                          SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_LATENCY,
                                                          SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_LATENCY):
            return float("inf")
        else:
            return (self.get_latency_predict(self.vnffgManager) - self.vnffgManager.sfc_req.sfc_qos['latency']).to(u.ms).value
