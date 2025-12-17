
import networkx as nx
import numpy as np
from astropy import units as u

from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager

class TrainEnvNet(nx.Graph):
    def __init__(self):
        super().__init__()
    
    def opt_node_attrs_value(self, node_id:int, node_attrs_name:str, opration:str, value=0) -> int:
        """Get the attribute values of a node

        Args:
            node_id (int): Networkx index of node
            node_attrs_name (str): "capacity/remain/request"+"_"+"cpu/ram/rom/band"
            opration (str): "get/set/decrease/increase"
            value(int): opration aim value
        Returns:
            int: value
        """
        remain_value = self.nodes[node_id][node_attrs_name]

        if opration == "get":
            return remain_value
        elif opration == "set":
            self.nodes[node_id][node_attrs_name] = value
        elif opration == "decrease":
            self.nodes[node_id][node_attrs_name] = remain_value - value
        elif opration == "increase":
            self.nodes[node_id][node_attrs_name] = remain_value + value
        
        return self.nodes[node_id][node_attrs_name]
    
    def get_all_nodes_attrs_values(self, node_attrs_name:str) -> list[int]:
        """Get the attribute values of all nodes in network

        Args:
            node_attrs_name (str): "capacity/remain/request"+"_"+"cpu/ram/rom/band"

        Returns:
            list[int]: values
        """

        return [self.nodes[node_id][node_attrs_name] for node_id in self.nodes]
    
    def get_all_nodes_aggrlinks_attrs_values(self, link_attrs_name:str) -> list[int]:
        """Get the attribute values of the links around all node aggregates

        Args:
            link_attrs_name (str): "capacity/remain/request"+"_"+"band"

        Returns:
            list[int]: values
        """

        links_aggr_attrs_of_nodes = []
        adjacency_mat = self.get_adjacency_matrix()

        for i in range(len(self.nodes)):
            sum_temp = 0
            for j in range(len(self.nodes)):
                if i == j:
                    continue
                
                if adjacency_mat[i,j] == 1:
                    sum_temp += self.opt_link_attrs_value((i,j),link_attrs_name,'get')
            links_aggr_attrs_of_nodes.append(sum_temp)

        return links_aggr_attrs_of_nodes
    
    def opt_link_attrs_value(self, link_id:tuple[int,int], link_attrs_name:str, opration:str, value=0) -> int:
        """Get the attribute values of a link

        Args:
            link_id (tuple[int,int]): Networkx index of link
            link_attrs_name (str): "capacity/remain/request"+"_"+"band"
            opration (str): "get/set/decrease/increase"
            value(int): opration aim value
        Returns:
            int: value
        """

        remain_value = self.edges[link_id][link_attrs_name]

        if opration == "get":
            return remain_value
        elif opration == "set":
            self.edges[link_id][link_attrs_name] = value
        elif opration == "decrease":
            self.edges[link_id][link_attrs_name] = remain_value - value
        elif opration == "increase":
            self.edges[link_id][link_attrs_name] = remain_value + value
        
        return self.edges[link_id][link_attrs_name]

    def get_all_links_attrs_values(self, link_attrs_name:str) -> dict[tuple[int,int]:int]:
        """Get the attribute values of all links in network

        Args:
            link_attrs_name (str): "capacity/remain/request"+"_"+"band"

        Returns:
            dict[tuple[int,int]:int]: edge:value
        """
        link_dict = {}
        for edge in self.edges:
            link_dict[(edge[0],edge[1])] = link_dict[(edge[1],edge[0])] = self.edges[edge][link_attrs_name]

        return link_dict

    def get_adjacency_matrix(self):
        adjacency_mat = np.zeros((len(self.nodes),len(self.nodes)))
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes)):
                if self.has_edge(i,j) and self.edges[(i,j)]["weight"] != np.inf:
                    adjacency_mat[i,j] = 1
        
        return adjacency_mat
    
    def get_kshortest_paths(self, source, target, k):
        from itertools import islice
        return list(islice(nx.shortest_simple_paths(self, source, target, weight='weight'), k))
    
    def get_djikstra_path(self, source, target):
        try:
            path = nx.dijkstra_path(self, source, target, weight='weight')
        except nx.NetworkXNoPath:
            path = []
        return path
    
    def get_path_weight(self, path):
        return sum([self.edges[path[i],path[i+1]]['weight'] for i in range(len(path)-1)])


class TrainEnvPNet(TrainEnvNet):
    def __init__(self,vnffgManager:"VnffgManager", solution_deploy:SolutionDeploy):
        super().__init__()

        env_current_topo:nx.Graph = solution_deploy.current_topo
        self.add_nodes_from(env_current_topo.nodes(data=True))
        
        for node_id in range(len(self.nodes)):
            self.nodes[node_id]["type"] = vnffgManager.vnfVim.nfvi_group[node_id].node_type
            
            self.nodes[node_id]["capacity_cpu"] = vnffgManager.vnfVim.nfvi_group[node_id].get_max_resource().get("cpu")
            self.nodes[node_id]["capacity_ram"] = vnffgManager.vnfVim.nfvi_group[node_id].get_max_resource().get("ram").to(u.GB).value
            self.nodes[node_id]["capacity_rom"] = vnffgManager.vnfVim.nfvi_group[node_id].get_max_resource().get("rom").to(u.GB).value
            
            self.nodes[node_id]["remain_cpu"] = vnffgManager.vnfVim.nfvi_group[node_id].get_remain_resource().get("cpu")
            self.nodes[node_id]["remain_ram"] = vnffgManager.vnfVim.nfvi_group[node_id].get_remain_resource().get("ram").to(u.GB).value
            self.nodes[node_id]["remain_rom"] = vnffgManager.vnfVim.nfvi_group[node_id].get_remain_resource().get("rom").to(u.GB).value
            
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes)):
                if i == j:
                    self.add_edge(i, j, capacity_band=np.inf, remain_band=np.inf, weight=1)
                    continue
                if env_current_topo.has_edge(i,j):
                    self.add_edge(i, j, 
                                  capacity_band=vnffgManager.vnfVim.nfvi_group[i].get_max_bandwidth().value, 
                                  remain_band=vnffgManager.vnfVim.nfvi_group[i].get_remain_bandwidth().value, 
                                  weight=env_current_topo.edges[(i,j)]["weight"])

    def get_resource_used_ratio(self, node_id:int) -> float:
        resource_used_ratio = 1.0
        cpu_used = self.nodes[node_id]["capacity_cpu"] - self.nodes[node_id]["remain_cpu"]
        ram_used = self.nodes[node_id]["capacity_ram"] - self.nodes[node_id]["remain_ram"]
        rom_used = self.nodes[node_id]["capacity_rom"] - self.nodes[node_id]["remain_rom"]
        resource_used_ratio *= (cpu_used/self.nodes[node_id]["capacity_cpu"]) 
        resource_used_ratio *= (ram_used/self.nodes[node_id]["capacity_ram"])
        resource_used_ratio *= (rom_used/self.nodes[node_id]["capacity_rom"])
        
        return resource_used_ratio
    
    def get_average_resource_used_ratio(self) -> float:
        resource_used_ratio_list = []
        for node_id in range(len(self.nodes)):
            resource_used_ratio_list.append(self.get_resource_used_ratio(node_id))
        
        return sum(resource_used_ratio_list)/len(resource_used_ratio_list)
    

class TrainEnvVNet(TrainEnvNet):
    def __init__(self,vnffgManager:"VnffgManager", solution_deploy:SolutionDeploy):
        super().__init__()
        
        vnfnum = len(vnffgManager.sfc_req.sfc_vnfs_type)
        temp_graph = nx.path_graph(vnfnum)
        self.__dict__['_node'] = temp_graph.__dict__['_node']
        self.__dict__['_adj'] = temp_graph.__dict__['_adj']

        for node_id in range(vnfnum):
            self.nodes[node_id]["request_cpu"] = solution_deploy.resource['cpu'][node_id]
            self.nodes[node_id]["request_ram"] = solution_deploy.resource['ram'][node_id].to(u.GB).value
            self.nodes[node_id]["request_rom"] = solution_deploy.resource['rom'][node_id].to(u.GB).value

        for edge_temp in self.edges:
            self.edges[edge_temp]["request_band"] = 0
            self.edges[edge_temp]["weight"] = 0

