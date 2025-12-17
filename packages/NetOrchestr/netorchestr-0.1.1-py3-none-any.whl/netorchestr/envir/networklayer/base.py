from netaddr import IPAddress, IPNetwork
from netorchestr.envir.base import OModule, OGate, OMessage, Ipv4Pkt

class IpManager:
    """IP地址管理器"""
    def __init__(self, ip_pool_str: str = '192.168.0.0/24'):
        self.ip_pool = IPNetwork(ip_pool_str)
        """IP地址池"""
        self.assigned_ips = set()
        """已分配的IP地址"""
        self.available_ips = [ip for ip in self.ip_pool 
                              if ip != self.ip_pool.network 
                              and ip != self.ip_pool.broadcast]
        """可用IP地址列表并排除网络地址和广播地址"""
        
    def check_ip_valid(self, ip_addr: IPAddress) -> bool:
        """验证IP地址有效性并分配"""
        if not isinstance(ip_addr, IPAddress):
            raise TypeError("IP地址必须是IPAddress类型")
            
        if ip_addr in self.assigned_ips:
            raise ValueError(f"IP地址 {ip_addr} 已被使用")
            
        if ip_addr not in self.available_ips:
            raise ValueError(f"IP地址 {ip_addr} 不在允许的地址池范围内")
            
        return True

    def get_next_available_ip(self) -> IPAddress:
        """获取下一个可用的IP地址"""
        for ip_addr in self.available_ips:
            if ip_addr not in self.assigned_ips:
                self.assigned_ips.add(ip_addr)
                return ip_addr
                
        raise RuntimeError("没有可用的IP地址了,地址池已耗尽")

    def release_ip(self, ip_addr: IPAddress):
        """释放IP地址"""
        if ip_addr in self.assigned_ips:
            self.assigned_ips.remove(ip_addr)


class NetworkProtocolBase(OModule):
    def __init__(self, name, ip_addr: IPAddress = None):
        super().__init__(name)
        
        self.ip_addr = ip_addr
        """当前实例使用的IP地址"""
            
        self.routing_table:dict[IPAddress,str] = {}
        """创建路由表, 表结构为{目的地址: 数据包转发的目的物理层端口名}"""
        
        self.routing_msg_cache:dict[IPAddress,list[str]] = {}
        """创建该路由上的报文缓存, 表结构为{目的地址: list[OMessage.id]}
        
        主要用于缓存发往目的地址的不同报文, 防止出现重复转发的情况引发网络风暴
        """

    def recv_msg(self, msg: OMessage, gate: OGate):
        if gate.name == "upperLayerIn":
            for gate in self.gates:
                if gate.name == "lowerLayerOut":
                    self.send_msg(msg, gate)
        elif gate.name == "lowerLayerIn":
            for gate in self.gates:
                if gate.name == "upperLayerOut":
                    self.send_msg(msg, gate)


class NetworkProtocolEndIpv4(NetworkProtocolBase):
    """端设备的网络层模块
    
    Note: 端设备的网络层模块只需要实现将数据包从上层到下层互传
    
    """
    def __init__(self, name, ip_addr: IPAddress = None):
        super().__init__(name, ip_addr)
        
    def recv_msg(self, msg: OMessage, gate: OGate):
        if gate.name == "upperLayerIn":
            for gate in self.gates:
                if gate.name == "lowerLayerOut":
                    self.send_msg(msg, gate)
        elif gate.name == "lowerLayerIn":            
            ipv4Pkt: Ipv4Pkt = msg.content
            dst_ip = ipv4Pkt.dst_ip
            
            if dst_ip == self.ip_addr:
                for gate in self.gates:
                    if gate.name == "upperLayerOut":
                        self.send_msg(msg, gate)
            else:
                self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' gets data packet with unknown destination IP '{dst_ip}', discarding data packet")


class NetworkProtocolMiddleIpv4(NetworkProtocolBase):
    """中间设备的网络层模块
    
    Note: 中间设备的网络层模块需要实现路由功能, 即根据目的地址选择下一跳的物理层端口
    
    """
    def __init__(self, name, ip_addr: IPAddress = None):
        super().__init__(name, ip_addr)
    
    def check_duplicate(self, dst_ip:IPAddress,msg:"OMessage") -> bool:
        """检查是否是重复数据包
        
        Args:
            dst_ip: 目的地址
            msg: 要检查的报文
            
        Returns:
            bool: True 表示是重复数据包, False 表示不是重复数据包
        """
        if msg.id in self.routing_msg_cache.get(dst_ip,[]):
            self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' gets duplicate data packet with destination IP '{dst_ip}', discarding data packet {msg.id}")
            return True
        else:
            self.routing_msg_cache.setdefault(dst_ip,[]).append(msg.id)
            return False
    
    def check_ttl(self, msg:"OMessage") -> bool:
        """检查报文中的 ttl 判断是否过期
        
        Args:
            msg: 要检查的报文
            
        Returns:
            bool: True 表示报文过期, False 表示报文未过期
        """
        now_time = self.scheduler.now
        send_time = float(msg.timestamp)
        ttl_time = float(msg.ttl)
        if now_time - send_time > ttl_time:
            self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' gets data packet {msg.id} with expired ttl, discarding data packet")
            return True
        else:
            return False
    
    def recv_msg(self, msg: OMessage, gate: OGate):
        if gate.name == "upperLayerIn":
            self.logger.error(f"{self.scheduler.now}: Module '{self.name}' should not receive data from upper layer, it should not have upper layer module") 
        elif gate.name == "lowerLayerIn":

            ipv4Pkt: Ipv4Pkt = msg.content
            dst_ip = ipv4Pkt.dst_ip
            if dst_ip in self.routing_table:
                if self.check_duplicate(dst_ip,msg) or self.check_ttl(msg):
                    # 该数据包已处理过或者过期, 丢弃
                    return
                output_port_name = self.routing_table[dst_ip]
                send_seccess = False
                for gate in self.gates:
                    if gate.name == "lowerLayerOut" and self.gates[gate][1].ofModule.name == output_port_name:
                        self.send_msg(msg, gate)
                        send_seccess = True
                        self.logger.info(f"{self.scheduler.now}: Module '{self.name}' forwards data packet with destination IP '{dst_ip}' to module '{output_port_name}'")
                if send_seccess == False:
                    self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' cannot find output port '{output_port_name}' for data packet with destination IP '{dst_ip}'")
            else:
                self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' gets data packet with unknown destination IP '{dst_ip}', discarding data packet")


class NetworkProtocolDuAAu(NetworkProtocolBase):
    """O-RAN 移动通信模型Du-AAU的网络层模块
    
    Note: Du 为数据单元(有线传输), AAU 为接入单元(无线传输)
    
    需特殊设计, 默认转发策略: 
    
    * 将来自有线传输端口的数据包, 从无线传输端口发出
    * 将来自无线传输端口的数据包, 从有线传输端口发出
    """
    
    def __init__(self, name, ip_addr: IPAddress = None):
        super().__init__(name, ip_addr)
    
    def recv_msg(self, msg: OMessage, gate: OGate):
        if gate.name == "upperLayerIn":
            self.logger.error(f"{self.scheduler.now}: Module '{self.name}' should not receive data from upper layer, it should not have upper layer module") 
        elif gate.name == "lowerLayerIn":
            for pre_outgate in self.gates:
                # 直接从另外一个端口转发
                if pre_outgate.name == "lowerLayerOut" and self.gates[pre_outgate][1].ofModule.name != self.gates[gate][1].ofModule.name:
                    self.send_msg(msg, pre_outgate)
                    

class NetworkProtocolLaser(NetworkProtocolBase):
    def __init__(self, name, ip_addr: IPAddress = None):
        """激光传输协议的网络层模块
        
        Args:
            name: 模块名
            ip_addr: IP地址, 默认为None, 应由外层模块分配IP地址
    
        Note: 需特殊设计, 默认转发策略: 
        
        * 将来自有线传输端口的数据包, 从激光传输端口发出
        * 将来自激光传输端口的数据包, 从有线传输端口发出
        """
        super().__init__(name, ip_addr)
    
    def recv_msg(self, msg: OMessage, gate: OGate):
        if gate.name == "upperLayerIn":
            self.logger.error(f"{self.scheduler.now}: Module '{self.name}' should not receive data from upper layer, it should not have upper layer module") 
        elif gate.name == "lowerLayerIn":
            for pre_outgate in self.gates:
                # 直接从另外一个端口转发
                if pre_outgate.name == "lowerLayerOut" and self.gates[pre_outgate][1].ofModule.name != self.gates[gate][1].ofModule.name:
                    self.send_msg(msg, pre_outgate)
