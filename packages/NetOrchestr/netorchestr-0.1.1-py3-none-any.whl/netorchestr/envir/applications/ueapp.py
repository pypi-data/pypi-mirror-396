
import random
from ipaddress import IPv4Address
from astropy import units as u
from netorchestr.envir.base import OGate, OMessage, Srv4Pkt
from netorchestr.envir.applications.simple import SimpleApp

class UeAppSrv4(SimpleApp):
    def __init__(self, name: str):
        super().__init__(name)
        
        self.performance_record:list[float] = []
        """节点的业务性能记录 (当该节点为SFC的末端时记录到达数据包的总经历时延)"""
    
    def recv_msg(self, msg:"OMessage", gate:"OGate"):
        if msg.sender == f"{self.name}Timer":
            src_ip = self.ofModule.networkLayer.ip_addr
            if src_ip == "192.168.0.1":
                segment_list = ["192.168.0.2", "192.168.5.11", "192.168.4.11", "192.168.3.11", "192.168.2.11", "192.168.1.11"]
                segment_left = len(segment_list)-1
                dst_ip = segment_list[segment_left]
                paload = "Hello, VnfAppSrv4!"
                
                content = Srv4Pkt(src_ip, dst_ip, segment_left, segment_list, paload)
                message = OMessage(f"{self.scheduler.now}", f"{self.name}", "Ue2App", content, f"{self.name}{self.pkt_count}")
                
                for gate in self.gates:
                    if gate.name == "lowerLayerOut":
                        self.send_msg(message, gate)
                        self.logger.log(event="-", time=self.scheduler.now, from_node=self.name, to_node=message.receiver, pkt_type="UeAppSrv4Pkt", 
                                        pkt_size=len(message), pkt_id=message.id, src_addr=src_ip, dst_addr=dst_ip)
                        
                        self.pkt_count += 1
                        self.clocktime.set_tick_interval(random.randint(1, 5)*u.min)
        elif gate.name == "lowerLayerIn":
            srvs4pkt:Srv4Pkt = msg.content
            if srvs4pkt.dst_ip == self.ofModule.networkLayer.ip_addr:
                # 数据包是发给自己的
                if srvs4pkt.segment_left == 0:
                    # 最后一个分段，直接处理
                    
                    self.performance_record.append(self.scheduler.now - float(msg.timestamp))
                    
                    self.logger.log(event="r", time=self.scheduler.now, from_node=msg.sender, to_node=msg.receiver, pkt_type="UeAppSrv4Pkt", 
                                    pkt_size=len(msg), pkt_id=msg.id, src_addr=srvs4pkt.src_ip, dst_addr=srvs4pkt.dst_ip, 
                                    pkt_delay=self.scheduler.now - float(msg.timestamp))
                else:
                    # 中间分段，用户不可能需要进行中继处理，传递异常
                    self.logger.debug(f"{self.scheduler.now}: Module '{self.name}' shoud not receive middle segment packet from {msg.sender}")
            else:
                # 数据包不是发给自己的，大概率是上一跳路由发生了错误，丢弃
                self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' get packet from {msg.sender} with invalid destination IP address {srvs4pkt.dst_ip}")


class UeAppSfc(SimpleApp):
    def __init__(self, name: str):
        super().__init__(name)
        
        self.clocktime.set_tick_interval(random.expovariate(1)*u.ms)
        
        self.performance_record:list[float] = []
        """节点的业务性能记录 (当该节点为SFC的末端时记录到达数据包的总经历时延)"""
        
        self.msg_pool:list[OMessage] = []
        """用于记录已经接收到的业务数据包, 用于过滤重复数据包"""

    def check_duplicate(self, msg:"OMessage") -> bool:
        """检查是否是重复数据包"""
        for m in self.msg_pool:
            if m.id == msg.id:
                return True
        self.msg_pool.append(msg)
        return False

    def recv_msg(self, msg:"OMessage", gate:"OGate"):
        if msg.sender == f"{self.name}Timer":
            src_ip = self.ofModule.networkLayer.ip_addr
            if src_ip in ["192.168.0.1", "192.168.0.3"]:
                # 判断是否是业务发起用户
                
                if src_ip == "192.168.0.1":
                    # 用户发出 SFC1 的业务数据
                    
                    segment_list = ["192.168.0.2", "192.168.3.11", "192.168.2.11", "192.168.1.11"]
                    segment_left = len(segment_list)-1
                    dst_ip = segment_list[segment_left]
                    paload = "Hello, UeAppSfc1!"
                    
                    content = Srv4Pkt(src_ip, dst_ip, segment_left, segment_list, paload)
                    message = OMessage(f"{self.scheduler.now}", f"{self.name}", "Ue2App", content, f"{self.name}{self.pkt_count}")
                elif src_ip == "192.168.0.3":
                    # 用户发出 SFC2 的业务数据
                    
                    segment_list = ["192.168.0.4", "192.168.2.11", "192.168.1.11"]
                    segment_left = len(segment_list)-1
                    dst_ip = segment_list[segment_left]
                    paload = "Hello, UeAppSfc2!"
                    
                    content = Srv4Pkt(src_ip, dst_ip, segment_left, segment_list, paload)
                    message = OMessage(f"{self.scheduler.now}", f"{self.name}", "Ue4App", content, f"{self.name}{self.pkt_count}")
                
                
                for gate in self.gates:
                    if gate.name == "lowerLayerOut":
                        self.send_msg(message, gate)
                        self.logger.log(event="-", time=self.scheduler.now, from_node=self.name, to_node=message.receiver, pkt_type="UeAppSrv4Pkt", 
                                        pkt_size=len(message), pkt_id=message.id, src_addr=src_ip, dst_addr=dst_ip)
                        
                        self.pkt_count += 1
                        self.clocktime.set_tick_interval(random.expovariate(1)*u.ms)
            
        elif gate.name == "lowerLayerIn":
            srvs4pkt:Srv4Pkt = msg.content
            if srvs4pkt.dst_ip == self.ofModule.networkLayer.ip_addr:
                # 数据包是发给自己的
                if srvs4pkt.segment_left == 0:
                    # 最后一个分段，直接处理
                    
                    if self.check_duplicate(msg):
                        # 重复数据包，丢弃
                        self.logger.debug(f"{self.scheduler.now}: Module '{self.name}' get duplicate msg {msg.id}")
                        return
                    
                    self.performance_record.append(self.scheduler.now - float(msg.timestamp))
                    
                    self.logger.log(event="r", time=self.scheduler.now, from_node=msg.sender, to_node=msg.receiver, pkt_type="UeAppSrv4Pkt", 
                                    pkt_size=len(msg), pkt_id=msg.id, src_addr=srvs4pkt.src_ip, dst_addr=srvs4pkt.dst_ip, 
                                    pkt_delay=self.scheduler.now - float(msg.timestamp))
                else:
                    # 中间分段，用户不可能需要进行中继处理，传递异常
                    self.logger.debug(f"{self.scheduler.now}: Module '{self.name}' shoud not receive middle segment packet from {msg.sender}")
            else:
                # 数据包不是发给自己的，大概率是上一跳路由发生了错误，丢弃
                self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' get packet from {msg.sender} with invalid destination IP address {srvs4pkt.dst_ip}")


class SfcReq:
    def __init__(self, **kwargs):
        """ SFC 请求类
        Args:
            id (int): SFC 请求 ID
            start_time (u.quantity): SFC 服务开始时间, 单位为 u.quantity
            end_time (u.quantity): SFC 服务结束时间, 单位为 u.quantity
            sfc_type (str): SFC 类型, 如 "Ue2Ue/UeAccess", "Ue2Cloud", "Cloud2Cloud"
            sfc_vnfs_type (list[type]): SFC 中使用的 VNF 模板类型列表
            sfc_vnfs_shared (list[bool]): SFC 中使用的 VNF 是否支持共享
            sfc_qos (dict[str,float]): SFC 各个 VNF 的 QoS 要求
                - key: "latency", value: 延迟要求, 如 100 * u.ms, 0.1
                - key: "overrate", value: 可靠性要求, 如 0.1
            sfc_trans_model (dict): SFC 传输模型
                - key: "type", value: 传输模型类型, 如 "Poisson", "Uniform", "Stable"
                - key: "interval", value: 传输间隔, 单位为 u.quantity, 如 1 * u.ms
                - key: "payload_size", value: 业务数据包大小, 单位为 u.quantity, 如 100 * u.kbit
            sfc_end_point (list): SFC 端点列表
        """
        self.id:int = kwargs.get("id", None)
        """SFC 请求 ID"""
        
        self.start_time:u.quantity = kwargs.get("start_time", None)
        """SFC 服务开始时间, 单位为 u.quantity"""
        
        self.end_time:u.quantity = kwargs.get("end_time", None)
        """SFC 服务结束时间, 单位为 u.quantity"""
        
        self.sfc_type:str = kwargs.get("sfc_type", None)
        """SFC 类型, 如 Ue2Ue/UeAccess, Ue2Cloud, Cloud2Cloud
        
        其中 带有 2 类型的 SFC 意味该 SFC 在部署成功后会开启传输服务, 并进行实时的资源调度
        带有 Access 类型的 SFC 意味该 SFC 仅用于 UE 接入, 并不参与业务流量的传输
        """
        
        self.sfc_vnfs_type:list[str] = kwargs.get("sfc_vnfs_type", None)
        """SFC 中使用的 VNF 模板类型列表"""
        
        self.sfc_vnfs_shared:list[bool] = kwargs.get("sfc_vnfs_shared", None)
        """SFC 中使用的 VNF 是否支持共享"""
        
        self.sfc_qos:dict[str,float] = kwargs.get("sfc_qos", None)
        """SFC 各个 VNF 的 QoS 要求
        - key: "latency", value: 延迟要求, 如 100 * u.ms
        - key: "overrate", value: 可靠性要求, 如 0.1
        """
        
        self.sfc_trans_model:dict = kwargs.get("sfc_trans_model", None)
        """SFC 传输模型
        - key: "type", value: 传输模型类型, 如 "Poisson", "Uniform", "Stable"
        - key: "interval", value: 传输间隔, 单位为 u.quantity, 如 1 * u.ms
        - key: "payload_size", value: 业务数据包大小, 单位为 u.quantity, 如 100 * u.kbit
        """
        
        self.sfc_end_point = kwargs.get("sfc_end_point", None)
        """SFC 端点列表
        - 对于 Ue2Ue/UeAccess 类型的 SFC, 长度为 2, 第一个元素为 UE1 的节点模型, 第二个元素为 UE2 的节点模型
        - 对于 Ue2Cloud 类型的 SFC, 长度为 1, 第一个元素为 UE 的节点模型
        - 对于 Cloud2Cloud 类型的 SFC, 长度为 0, 无端点
        """
        
        if self.sfc_type in ["Ue2Ue","UeAccess"]:
            if len(self.sfc_end_point)!= 2:
                raise ValueError("Sfc with type 'Ue2Ue' sfc_end_point should have 2 elements")
        elif self.sfc_type == "Ue2Cloud":
            if len(self.sfc_end_point)!= 1:
                raise ValueError("Sfc with type 'Ue2Cloud' sfc_end_point should have 1 element")
        elif self.sfc_type == "Cloud2Cloud":
            if self.sfc_end_point is not None:
                raise ValueError("Sfc with type 'Cloud2Cloud' sfc_end_point should be None")

    @staticmethod
    def get_sfc_shared(qos_level, sfc_length) -> list[bool]:
        if sfc_length <= 0:
            return []
        
        if qos_level == "URLLC":
            # URLLC必须全为False
            return [False] * sfc_length
        elif qos_level == "mMTC":
            # mMTC一半为True，尽可能处于中间位置
            true_count = sfc_length // 2
            result = [False] * sfc_length
            
            # 计算起始索引，使True值集中在中间
            if sfc_length % 2 == 0:
                start = (sfc_length // 2) - (true_count // 2)
            else:
                start = (sfc_length // 2) - (true_count // 2)
            
            # 填充True值
            for i in range(true_count):
                position = start + i
                # 确保不超出列表范围（处理边界情况）
                if position < sfc_length:
                    result[position] = True
            
            return result
        elif qos_level == "eMBB":
            # eMBB必须全为True
            return [True] * sfc_length
        else:
            raise ValueError("qos_level must be 'URLLC','mMTC' or 'eMBB'")

class UeAppSfcDefine(SimpleApp):
    def __init__(self, name: str):
        super().__init__(name)
        
        self.clocktime.set_tick_interval(random.expovariate(1)*u.ms)
        
        self.performance_record:list[float] = []
        """节点的业务性能记录 (当该节点为SFC的末端时记录到达数据包的总经历时延)"""
        
        self.msg_pool:list[str] = []
        """用于记录已经接收到的业务数据包的id, 用于过滤重复数据包"""
        
        self.sfc_segment_list:list[IPv4Address] = None
        self.sfc_trans_model:dict = None

    def set_sfc_trans_task(self, sfc_req:SfcReq, segment_list:list[IPv4Address], receiver:str):
        """设置 SFC 传输任务"""
        self.sfc_req = sfc_req
        self.sfc_segment_list = segment_list
        self.sfc_trans_model = sfc_req.sfc_trans_model
        self.sfc_receiver = receiver
    
    def del_sfc_trans_task(self):
        """删除 SFC 传输任务"""
        self.sfc_req = None
        self.sfc_segment_list = None
        self.sfc_trans_model = None
        self.sfc_receiver = None
        
    def make_paload_with_sizelimit(self, size:u.quantity) -> str:
        """生成给定大小的业务数据"""
        # 转换为字节数
        byte_count = int(size.to(u.byte).value)
        
        if byte_count <= 0:
            return ""
        
        # 选择一个基础字符（不需要随机时可固定为一个字符）
        # 若完全不需要随机可改为固定字符如 'a'
        base_char = random.choice("abcdefghijklmnopqrstuvwxyz")
        
        # 使用字符串乘法高效生成指定长度的字符串
        # 计算完整块和剩余部分
        block_size = 1024  # 块大小可根据需要调整
        full_blocks = byte_count // block_size
        remainder = byte_count % block_size
        
        # 构建完整块 + 剩余部分
        payload = base_char * block_size * full_blocks + base_char * remainder
        
        return payload

    def check_duplicate(self, msg:"OMessage") -> bool:
        """检查是否是重复数据包
        
        Args:
            msg (OMessage): 待检查的消息
        
        Returns:
            bool: True 表示是重复数据包, False 表示不是重复数据包
        """
        if msg.id in self.msg_pool:
            self.logger.debug(f"{self.scheduler.now}: Module '{self.name}' get duplicate msg {msg.id}")
            return True
        else:
            self.msg_pool.append(msg.id)
            return False
    
    def recv_msg(self, msg:"OMessage", gate:"OGate"):
        if msg.sender == f"{self.name}Timer":
            if self.sfc_segment_list is None or self.sfc_trans_model is None:
                self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' can not send packet without sfc segment list or trans model")
                return
            
            src_ip = self.ofModule.networkLayer.ip_addr
            segment_list = self.sfc_segment_list
            segment_left = len(segment_list)-1
            dst_ip = segment_list[segment_left]
            paload = self.make_paload_with_sizelimit(self.sfc_trans_model['payload_size'])
            content = Srv4Pkt(src_ip, dst_ip, segment_left, segment_list, paload)
            message = OMessage(timestamp=f"{self.scheduler.now}", 
                               sender=f"{self.name}", 
                               receiver=self.sfc_receiver, 
                               content=content, 
                               id=f"{self.name}{self.pkt_count}",
                               ttl=f"{self.sfc_req.sfc_qos.get('latency').to(u.ms).value*3}")
            
            for gate in self.gates:
                if gate.name == "lowerLayerOut":
                    self.send_msg(message, gate)
                    self.logger.log(event="-", time=self.scheduler.now, from_node=self.name, to_node=message.receiver, pkt_type="UeAppSrv4Pkt", 
                                    pkt_size=len(message), pkt_id=message.id, src_addr=src_ip, dst_addr=dst_ip)
                    
                    self.pkt_count += 1
                    
                    interval_time_ms = self.sfc_trans_model['interval'].to(u.ms).value
                    if self.sfc_trans_model['type'] == 'Poisson':
                        lambda_param = 1.0/interval_time_ms
                        self.clocktime.set_tick_interval(random.expovariate(lambda_param)*u.ms)
                    elif self.sfc_trans_model['type'] == 'Uniform':
                        self.clocktime.set_tick_interval(random.uniform(interval_time_ms/2, interval_time_ms)*u.ms)
                    elif self.sfc_trans_model['type'] == 'Stable':
                        self.clocktime.set_tick_interval(interval_time_ms*u.ms)
                    else:
                        raise ValueError(f"Unsupported sfc trans model type: {self.sfc_trans_model['type']}")
                    
        elif gate.name == "lowerLayerIn":
            srvs4pkt:Srv4Pkt = msg.content
            if srvs4pkt.dst_ip == self.ofModule.networkLayer.ip_addr:
                # 数据包是发给自己的，待判断是重复丢弃、中继处理还是最终处理
                
                if self.check_duplicate(msg):
                    # 重复数据包，丢弃
                    return

                if srvs4pkt.segment_left == 0:
                    # 最后一个分段，直接处理                    
                    self.performance_record.append(self.scheduler.now - float(msg.timestamp))
                    
                    self.logger.log(event="r", time=self.scheduler.now, from_node=msg.sender, to_node=msg.receiver, pkt_type="UeAppSrv4Pkt", 
                                    pkt_size=len(msg), pkt_id=msg.id, src_addr=srvs4pkt.src_ip, dst_addr=srvs4pkt.dst_ip, 
                                    pkt_delay=self.scheduler.now - float(msg.timestamp))
                else:
                    # 中间分段，用户不可能需要进行中继处理，传递异常
                    self.logger.debug(f"{self.scheduler.now}: Module '{self.name}' shoud not receive middle segment packet from {msg.sender}")
            else:
                # 数据包不是发给自己的，大概率是上一跳路由发生了错误，丢弃
                self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' get packet from {msg.sender} with invalid destination IP address {srvs4pkt.dst_ip}")

