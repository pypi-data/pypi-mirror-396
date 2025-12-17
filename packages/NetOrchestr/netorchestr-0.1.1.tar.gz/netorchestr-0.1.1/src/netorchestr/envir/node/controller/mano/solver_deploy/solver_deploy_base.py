#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   solver.py
@Time    :   2024/06/18 15:32:23
@Author  :   Wang Xi
@Version :   0.0
@Contact :   wangxi_chn@foxmail.com
@License :   (C)Copyright 2023-2024, Wang Xi
@Desc    :   None
'''

from enum import Enum, auto
import numpy as np
import copy
import networkx as nx

from astropy import units as u

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import NfvOrchestrator, VnffgManager

class SOLUTION_DEPLOY_TYPE(Enum):
    NOTHING = auto()
    SET_SUCCESS = auto()
    SET_FAILED_FOR_NODE_CPU = auto()
    SET_FAILED_FOR_NODE_RAM = auto()
    SET_FAILED_FOR_NODE_ROM = auto()
    SET_FAILED_FOR_LINK_BAND = auto()
    SET_FAILED_FOR_LATENCY = auto()
    SET_FAILED_FOR_UE_ACCESS_START = auto()
    SET_FAILED_FOR_UE_ACCESS_END = auto()
    SET_FAILED_FOR_NO_PATH = auto()
    CHANGE_SUCCESS = auto()
    CHANGE_FAILED_FOR_NODE_CPU = auto()
    CHANGE_FAILED_FOR_NODE_RAM = auto()
    CHANGE_FAILED_FOR_NODE_ROM = auto()
    CHANGE_FAILED_FOR_LINK_BAND = auto()
    CHANGE_FAILED_FOR_LATENCY = auto()
    CHANGE_FAILED_FOR_UE_ACCESS_START = auto()
    CHANGE_FAILED_FOR_UE_ACCESS_END = auto()
    CHANGE_FAILED_FOR_NO_PATH = auto()
    END_SUCCESS = auto()

class SolutionDeploy:
    def __init__(self) -> None:
        self.current_time:float = None
        """该编排方案得到的结果的当前时间, 为 simpy 仿真时间, 单位为 ms"""
        
        self.current_topo:nx.Graph = None
        self.current_topo_with_ue:nx.Graph = None
        self.current_req_type:str = None
        self.current_qos:dict[str,u.Quantity] = {}
        self.current_result: bool = False
        self.current_description :SOLUTION_DEPLOY_TYPE = SOLUTION_DEPLOY_TYPE.NOTHING

        self.map_node: dict[int,int] = {}
        """dict[vnf:nfvi]
        Description: map from VNF nodes to NFVI nodes
        """
        
        self.share_node: list[int] = []
        """list[VnfEm.id]
        Description: the exisiting VNF nodes that is shared by self
        """

        self.map_link: dict[tuple[int,int],list[tuple[int,int]]] = {}
        """dict[vnf.link:list[nfvi.link]]
        Description: map from VNF links to NFVI links
        """

        self.resource: dict[str,list[int]] = {}
        """dict[resource name:list[value]]
        Description: the resources allocated on each VNF and link between VNFs
        
        Example:
        
            {
                'cpu': [1, 0.5, 2],
                'ram': [256 * u.MB, 512 * u.MB, 256 * u.MB],
                'rom': [1024 * u.GB, 1024 * u.GB, 1024 * u.GB],
            }
        """
        
        self.current_latency: u.Quantity = 0 * u.ms
        """u.Quantity
        Description: the current latency of the solution
        """
        
        self.cost_resource:float = 0.0
        self.cost_migration:float = 0.0
        
        self.revenue:float = 0.0
        
        

class SolverDeployBase:
    def __init__(self, name:str):
        self.name = name
        
        self.work_mode = "to_be_defined"
        """求解器工作模型, 通常被用于智能算法类求解器用来区分训练模式和验证模式"""

    def ready_for_controller(self, nfvOrchestrator:"NfvOrchestrator"):
        self.nfvOrchestrator = nfvOrchestrator

    def solve_embedding(self,vnffgManager:"VnffgManager") -> SolutionDeploy:
        return NotImplementedError
    
    def solve_migration(self,vnffgManager:"VnffgManager") -> SolutionDeploy:
        return NotImplementedError
    
    def solve_ending(self,vnffgManager:"VnffgManager") -> SolutionDeploy:
        self.vnffgManager = vnffgManager
        
        # 继承上一次编排方案的结果
        self.solution_deploy:SolutionDeploy = copy.deepcopy(vnffgManager.solutions_deploy[-1])
        # 修正本次编排方案的请求类型
        self.solution_deploy.current_req_type = "leave"
        # 修正本次编排方案的记录时间
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        
        self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.END_SUCCESS
        self.solution_deploy.current_result = True
        
        # 结算成本和收益
        self.calculate_cost_and_revenue(vnffgManager)

        return self.solution_deploy
    
    def check_solution(self, vnffgManager:"VnffgManager") -> SOLUTION_DEPLOY_TYPE:
        """检查求解器的输出解是否满足约束条件

        Args:
            vnffgManager (VnffgManager): 包含了当前的 VNFFG 信息
        
        Returns:
            SOLUTION_DEPLOY_TYPE: 返回求解器的输出解是否满足约束条件的结果
        """
                
        nfvi_group_remain_resource_cpu_copy = copy.deepcopy([nfvi.resource_remain['cpu'] for nfvi in vnffgManager.vnfVim.nfvi_group.values()])
        nfvi_group_remain_resource_ram_copy = copy.deepcopy([nfvi.resource_remain['ram'] for nfvi in vnffgManager.vnfVim.nfvi_group.values()])
        nfvi_group_remain_resource_rom_copy = copy.deepcopy([nfvi.resource_remain['rom'] for nfvi in vnffgManager.vnfVim.nfvi_group.values()])
        
        for vnf_index, nfvi_id in self.solution_deploy.map_node.items():

            if nfvi_group_remain_resource_cpu_copy[nfvi_id] < \
                self.solution_deploy.resource['cpu'][vnf_index]:
                    if self.solution_deploy.current_req_type == 'arrive':
                        return SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_CPU
                    elif self.solution_deploy.current_req_type == 'migrate':
                        return SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_CPU
            
            nfvi_group_remain_resource_cpu_copy[nfvi_id] -= self.solution_deploy.resource['cpu'][vnf_index]
            
            if nfvi_group_remain_resource_ram_copy[nfvi_id] < \
                self.solution_deploy.resource['ram'][vnf_index]:
                    if self.solution_deploy.current_req_type == 'arrive':
                        return SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_RAM
                    elif self.solution_deploy.current_req_type == 'migrate':
                        return SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_RAM
            
            nfvi_group_remain_resource_ram_copy[nfvi_id] -= self.solution_deploy.resource['ram'][vnf_index]
                    
            if nfvi_group_remain_resource_rom_copy[nfvi_id] < \
                self.solution_deploy.resource['rom'][vnf_index]:
                    if self.solution_deploy.current_req_type == 'arrive':
                        return SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_ROM
                    elif self.solution_deploy.current_req_type == 'migrate':
                        return SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_ROM
                    
            nfvi_group_remain_resource_rom_copy[nfvi_id] -= self.solution_deploy.resource['rom'][vnf_index]

        for vnfpair_index, path in self.solution_deploy.map_link.items():
            foward_nfvi_id = []
            for sub_path in path:
                foward_nfvi_id += list(sub_path)
            foward_nfvi_id = list(set(foward_nfvi_id[:-1])) # 去掉该子段路由上的尾 NFVI 节点并去重
            
            for nfvi_id in foward_nfvi_id:
                nfvi = vnffgManager.vnfVim.nfvi_group[nfvi_id]
                vnf_index = vnfpair_index[0]
                vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_index]
                vnf_rate_per_cpu = vnffgManager.vnfManager.vnfTemplates[vnf_type].rate_per_core
                need_bandwidth = self.solution_deploy.resource['cpu'][vnf_index] * vnf_rate_per_cpu * \
                                 vnffgManager.sfc_req.sfc_trans_model['payload_size'] / u.ms
                                    
                if nfvi.get_remain_bandwidth() < need_bandwidth:
                    if self.solution_deploy.current_req_type == 'arrive':
                        return SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_LINK_BAND
                    elif self.solution_deploy.current_req_type == 'migrate':
                        return SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_LINK_BAND
        
        # Qos Constraint Check
        self.solution_deploy.current_latency = self.get_latency_predict(vnffgManager)
        if self.solution_deploy.current_latency > vnffgManager.sfc_req.sfc_qos.get("latency"):
            if self.solution_deploy.current_req_type == 'arrive':
                return SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_LATENCY
            elif self.solution_deploy.current_req_type == 'migrate':
                return SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_LATENCY
        
        # All check passed
        if self.solution_deploy.current_req_type == 'arrive': 
            return SOLUTION_DEPLOY_TYPE.SET_SUCCESS
        elif self.solution_deploy.current_req_type == 'migrate': 
            return SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS
    
    def get_latency_predict(self, vnffgManager:"VnffgManager", direct:bool=True) -> u.quantity:
        """获取端到端的传播时延累积

        Args:
            vnffgManager (VnffgManager): VNFFG管理器

        Returns:
            u.quantity: 传播时延累积值
        """
        if not direct:
            # 此时为外部请求测量，需从 vnffgManager.solutions_deploy 提取最新的部署结果避免同一控制器的相互影响
            # 外部请求处理主要用于实时监测该 SFC 是否发生了断连
            self.solution_deploy:SolutionDeploy = copy.deepcopy(vnffgManager.solutions_deploy[-1])
        else:
            # 此时为内部请求测量，直接使用当前部署结果，最新的部署已保存在 self.solution_deploy 中
            pass
        
        latency_list = []
        for phy_link_list in self.solution_deploy.map_link.values():
            for phy_link in phy_link_list:
                nfvi_1 = vnffgManager.vnfVim.nfvi_group[phy_link[0]]
                nfvi_2 = vnffgManager.vnfVim.nfvi_group[phy_link[1]]
                latency_list.append(vnffgManager.vnfVim.get_latency_between_nfvi_node(nfvi_1, nfvi_2))

        ue_access_start = vnffgManager.ue_access_start
        nfvi_access_start = vnffgManager.vnfVim.nfvi_group[list(self.solution_deploy.map_node.values())[0]]
        
        _, _, latency = vnffgManager.vnfVim.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue_access_start.node_handle.radioPhy,
                                                                                                                      nfvi_access_start.node_handle.duAau.radioPhy)
        latency_list.append(latency)
            
        ue_access_end = vnffgManager.ue_access_end
        nfvi_access_end = vnffgManager.vnfVim.nfvi_group[list(self.solution_deploy.map_node.values())[-1]]
        
        _, _, latency = vnffgManager.vnfVim.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue_access_end.node_handle.radioPhy,
                                                                                                                      nfvi_access_end.node_handle.duAau.radioPhy)
        latency_list.append(latency)
        
        if sum(latency_list) == np.inf * u.ms and direct:
            # 如果是内部请求，且没有路径可达，则说明在部署时就处理不当，需要仔细检查
            # import code
            # code.interact(local=locals())
            print(f"\nWARNING: {self.__class__.__name__} 求解器检查处理内部请求时出现没有路径可达的情况, 则说明在部署时就处理不当, 需要仔细检查")

        return sum(latency_list)
    
    def calculate_cost_and_revenue(self, vnffgManager:"VnffgManager") -> list[float]:
        """计算服务成本和收益

        Args:
            vnffgManager (VnffgManager): VNFFG管理器
            
        Returns:
            float: 服务成本和收益
        """
        if len(vnffgManager.solutions_deploy) == 0:
            # 此时为初始部署，还未产生服务时长因此无需计算资源消耗
            return [0.0, 0.0]
        
        solution_deploy_last = vnffgManager.solutions_deploy[-1]
        solution_deploy_now = self.solution_deploy
        
        if self.solution_deploy.current_req_type == 'arrive':
            pass
        elif self.solution_deploy.current_req_type == 'migrate':
            if self.solution_deploy.current_result == True:
                # 迁移成功
                solution_deploy_now.cost_migration = solution_deploy_last.cost_migration + self._calculate_migration_cost(vnffgManager)
                solution_deploy_now.cost_resource = solution_deploy_last.cost_resource + self._calculate_resource_cost(vnffgManager)
                solution_deploy_now.revenue = solution_deploy_last.revenue + self._calculate_revenue(vnffgManager)
            else:
                # 迁移失败
                solution_deploy_now.cost_migration = solution_deploy_last.cost_migration
                solution_deploy_now.cost_resource = solution_deploy_last.cost_resource + self._calculate_resource_cost(vnffgManager)
                solution_deploy_now.revenue = solution_deploy_last.revenue + self._calculate_revenue(vnffgManager)
        elif self.solution_deploy.current_req_type == 'leave':
            # 结束部署
            solution_deploy_now.cost_migration = solution_deploy_last.cost_migration
            solution_deploy_now.cost_resource = solution_deploy_last.cost_resource + self._calculate_resource_cost(vnffgManager)
            solution_deploy_now.revenue = solution_deploy_last.revenue + self._calculate_revenue(vnffgManager)
        else:
            raise ValueError(f"{self.__class__.__name__} report: Invalid request type")
        
        return [solution_deploy_now.cost_migration+solution_deploy_now.cost_resource, solution_deploy_now.revenue]
        
    
    def _calculate_resource_cost(self, vnffgManager:"VnffgManager") -> float:
        """计算随时间累积的资源成本

        Args:
            vnffgManager (VnffgManager): VNFFG管理器

        Returns:
            float: 资源消耗成本
        """
        if len(vnffgManager.solutions_deploy) == 0:
            # 此时为初始部署，还未产生服务时长因此无需计算资源消耗
            return 0
        
        solution_deploy_last = vnffgManager.solutions_deploy[-1]
        solution_deploy_now = self.solution_deploy
        sfc_service_time = solution_deploy_now.current_time - solution_deploy_last.current_time
        sfc_service_time = (sfc_service_time*u.ms).to(u.s).value
        
        # 计算单位时间 SFC 节点资源消耗
        sfc_resource_cost_node_per_time = 0
        for vnf_index, nfvi_id in solution_deploy_last.map_node.items():
            # 获取由于部署平台的差异化造成的资源消耗倍乘系数
            vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_index]
            vnf_init_loc_type = vnffgManager.vnfVim.nfvi_group[nfvi_id].node_type
            vnf_resource_cost_factor = vnffgManager.vnfManager.vnfTemplates[vnf_type].cost_with_loc[vnf_init_loc_type]
            
            vnf_resource_cost_per_time = 1
            vnf_resource_cost_per_time = vnf_resource_cost_per_time * (solution_deploy_last.resource['cpu'][vnf_index] * vnf_resource_cost_factor)
            vnf_resource_cost_per_time = vnf_resource_cost_per_time * (solution_deploy_last.resource['ram'][vnf_index].to(u.GB).value * vnf_resource_cost_factor)
            if solution_deploy_last.share_node[vnf_index] == None: # 非共享节点需新增加 ROM 类型资源消耗
                vnf_resource_cost_per_time = vnf_resource_cost_per_time * (solution_deploy_last.resource['rom'][vnf_index].to(u.GB).value * vnf_resource_cost_factor)
        
            sfc_resource_cost_node_per_time += vnf_resource_cost_per_time
        
        # 计算单位时间 SFC 链路资源消耗
        sfc_resource_cost_link_per_time = 0
        for vnfpair_index, path in solution_deploy_last.map_link.items():
            band_need = (vnffgManager.sfc_req.sfc_trans_model["payload_size"].to(u.Mbit) / vnffgManager.sfc_req.sfc_trans_model["interval"].to(u.s)).value
            sfc_resource_cost_link_per_time += len(path) * band_need
            
        sfc_resource_cost_per_time = sfc_resource_cost_node_per_time * sfc_resource_cost_link_per_time
        
        # 计算服务时间内累积资源消耗
        sfc_resource_cost = sfc_resource_cost_per_time * sfc_service_time
        
        
                
        return sfc_resource_cost
    
    def _calculate_migration_cost(self, vnffgManager:"VnffgManager") -> float:
        """计算当 SFC 需要重部署的迁移成本

        Args:
            vnffgManager (VnffgManager): VNFFG管理器

        Returns:
            float: 迁移成本
        """
        if len(vnffgManager.solutions_deploy) == 0:
            # 此时为初始部署，无需计算迁移成本
            return 0
        
        solution_deploy_last = vnffgManager.solutions_deploy[-1]
        solution_deploy_now = self.solution_deploy
        sfc_service_time = solution_deploy_now.current_time - solution_deploy_last.current_time
        sfc_service_time = (sfc_service_time*u.ms).to(u.s).value
        
        # 计算节点迁移成本
        sfc_migration_cost_node = 0
        for vnf_index, nfvi_id in solution_deploy_now.map_node.items():
            if solution_deploy_last.map_node[vnf_index] != solution_deploy_now.map_node[vnf_index]:
                # 获取由于部署平台的差异化造成的资源消耗倍乘系数
                vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_index]
                vnf_init_loc_type = vnffgManager.vnfVim.nfvi_group[nfvi_id].node_type
                vnf_resource_cost_factor = vnffgManager.vnfManager.vnfTemplates[vnf_type].cost_with_loc[vnf_init_loc_type]
                
                vnf_migration_cost = 1
                vnf_migration_cost = vnf_migration_cost * (solution_deploy_now.resource['cpu'][vnf_index] * vnf_resource_cost_factor)
                vnf_migration_cost = vnf_migration_cost * (solution_deploy_now.resource['ram'][vnf_index].to(u.GB).value * vnf_resource_cost_factor)
                if solution_deploy_now.share_node[vnf_index] == None:
                    vnf_migration_cost = vnf_migration_cost * (solution_deploy_now.resource['rom'][vnf_index].to(u.GB).value * vnf_resource_cost_factor)
                
                sfc_migration_cost_node += vnf_migration_cost
        
        # 计算链路迁移成本
        sfc_migration_cost_link = 0    
        for vnfpair_index, path in solution_deploy_now.map_link.items():
            if solution_deploy_last.map_link.get(vnfpair_index) != solution_deploy_now.map_link.get(vnfpair_index):
                band_need = (vnffgManager.sfc_req.sfc_trans_model["payload_size"].to(u.Mbit) / vnffgManager.sfc_req.sfc_trans_model["interval"].to(u.s)).value
                sfc_migration_cost_link += len(path) * band_need
        # 防止连乘因子为 0
        sfc_migration_cost_link = 1 if sfc_migration_cost_link == 0 else sfc_migration_cost_link

        sfc_migration_cost = sfc_migration_cost_node * sfc_migration_cost_link
                                
        return sfc_migration_cost
    
    def _calculate_revenue(self, vnffgManager:"VnffgManager") -> float:
        """计算当 SFC 服务结束时得到的累积收益

        Args:
            vnffgManager (VnffgManager): VNFFG管理器

        Returns:
            float: 收益
        """
        if len(vnffgManager.solutions_deploy) == 0:
            # 此时为初始部署，无需计算收益
            return 0
        
        solution_deploy_last = vnffgManager.solutions_deploy[-1]
        solution_deploy_now = self.solution_deploy
        sfc_service_time = solution_deploy_now.current_time - solution_deploy_last.current_time
        sfc_service_time = (sfc_service_time*u.ms).to(u.s).value
        
        # 服务满意度
        sfc_satisfaction = 1 - (solution_deploy_last.current_latency / vnffgManager.sfc_req.sfc_qos["latency"])
        # 服务可靠性
        packet_over_latency_rate = vnffgManager.sfc_req.sfc_qos["overrate"]
        sfc_reliability = np.exp(-packet_over_latency_rate/vnffgManager.sfc_req.sfc_qos["overrate"])
        # 用户流量需求
        sfc_req_traffic = (vnffgManager.sfc_req.sfc_trans_model["payload_size"].to(u.Mbit) / vnffgManager.sfc_req.sfc_trans_model["interval"].to(u.s)).value
        sfc_req_traffic *= (len(vnffgManager.sfc_req.sfc_vnfs_type)-1)
        # 用户资源需求
        sfc_req_resource = 0
        for vnf_index, nfvi_id in solution_deploy_last.map_node.items():            
            vnf_resource_cost_per_time = 1
            vnf_resource_cost_per_time *= (solution_deploy_last.resource['cpu'][vnf_index])
            vnf_resource_cost_per_time *= (solution_deploy_last.resource['ram'][vnf_index].to(u.GB).value)
            vnf_resource_cost_per_time *= (solution_deploy_last.resource['rom'][vnf_index].to(u.GB).value)
            
            sfc_req_resource += vnf_resource_cost_per_time
        
        # 单位时间的 SFC 收益
        sfc_revenue_per_time = sfc_req_traffic * sfc_satisfaction * sfc_reliability * sfc_req_resource
        # 计算服务时间内累积收益
        sfc_revenue = sfc_revenue_per_time * sfc_service_time
                
        return sfc_revenue
    
    def save_param(self):
        pass

    def load_param(self):
        pass


class SolverDeploySharedBase(SolverDeployBase):
    def __init__(self, name:str):
        super().__init__(name)
        
    def solve_embedding(self,vnffgManager:"VnffgManager") -> SolutionDeploy:
        if vnffgManager.sfc_req.id == 0:
        
            self.vnffgManager = vnffgManager
            self.solution_deploy = SolutionDeploy()
            self.solution_deploy.current_req_type = "arrive"
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

            self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
            
            self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)

            self.solution_deploy.map_node = {self.current_vnfs_index_list[0]:self.current_nfvi_index_list[0],
                                             self.current_vnfs_index_list[1]:self.current_nfvi_index_list[1],
                                             self.current_vnfs_index_list[2]:self.current_nfvi_index_list[2]}
            
            self.solution_deploy.map_link = {(0,1):[(self.current_nfvi_index_list[0],self.current_nfvi_index_list[1])],
                                             (1,2):[(self.current_nfvi_index_list[1],self.current_nfvi_index_list[2])]}
        
            # algorithm end ---------------------------------------------

            self.solution_deploy.current_description = self.check_solution(vnffgManager)

            if self.solution_deploy.current_description != SOLUTION_DEPLOY_TYPE.SET_SUCCESS:
                self.solution_deploy.current_result = False
            else:
                self.solution_deploy.current_result = True

            return self.solution_deploy
        
        else:
            
            self.solution_deploy = SolutionDeploy()
            self.current_nfvi_index_list = list(vnffgManager.vnfVim.nfvi_group.keys())
            self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
            
            # algorithm begin ---------------------------------------------
            
            self.solution_deploy.map_node = {self.current_vnfs_index_list[0]:self.current_nfvi_index_list[0],
                                             self.current_vnfs_index_list[1]:self.current_nfvi_index_list[1]}
            
            self.solution_deploy.map_link = {(0,1):[(self.current_nfvi_index_list[0],self.current_nfvi_index_list[1])]}
            
            shared_vnfem_1 = vnffgManager.vnfVim.nfvi_group[self.current_nfvi_index_list[0]].deployed_vnf[0]
            shared_vnfem_2 = vnffgManager.vnfVim.nfvi_group[self.current_nfvi_index_list[1]].deployed_vnf[0]
            self.solution_deploy.share_node = [shared_vnfem_1.id, shared_vnfem_2.id]
            
            self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu'] 
                                            for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
            self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram'] 
                                            for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
            self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                            for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
            
            # algorithm end ---------------------------------------------

            self.solution_deploy.current_description = self.check_solution(vnffgManager)

            if self.solution_deploy.current_description != SOLUTION_DEPLOY_TYPE.SET_SUCCESS:
                self.solution_deploy.current_result = False
            else:
                self.solution_deploy.current_result = True

            return self.solution_deploy

    def solve_migration(self,vnffgManager:"VnffgManager") -> SolutionDeploy:
        if vnffgManager.sfc_req.id == 0:
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
            
            self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
            
            self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
            
            self.solution_deploy.map_node = {self.current_vnfs_index_list[0]:self.current_nfvi_index_list[0],
                                             self.current_vnfs_index_list[1]:self.current_nfvi_index_list[1],
                                             self.current_vnfs_index_list[2]:self.current_nfvi_index_list[2]}
            
            self.solution_deploy.map_link = {(0,1):[(self.current_nfvi_index_list[0],self.current_nfvi_index_list[1])],
                                             (1,2):[(self.current_nfvi_index_list[1],self.current_nfvi_index_list[2])]}
            
            # shared_vnfem_1 = vnffgManager.vnfVim.nfvi_group[self.current_nfvi_index_list[0]].deployed_vnf[0]
            # shared_vnfem_2 = vnffgManager.vnfVim.nfvi_group[self.current_nfvi_index_list[1]].deployed_vnf[0]
            
            self.solution_deploy.share_node = [None, None, None]
            
            # algorithm end ---------------------------------------------

            self.solution_deploy.current_description = self.check_solution(vnffgManager)

            if self.solution_deploy.current_description != SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS:
                self.solution_deploy.current_result = False
            else:
                self.solution_deploy.current_result = True

            return self.solution_deploy






