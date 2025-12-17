
import random
from astropy import units as u
from netorchestr.envir.base import OGate, OMessage, Ipv4Pkt, Srv4Pkt
from netorchestr.envir.applications.simple import SimpleApp

class VnfAppIpv4(SimpleApp):
    def __init__(self, name: str):
        super().__init__(name)
    
    def recv_msg(self, msg:"OMessage", gate:"OGate"):
        if msg.sender == f"{self.name}Timer":
            for gate in self.gates:
                if gate.name == "lowerLayerOut":
                    src_ip = self.ofModule.networkLayer.ip_addr
                    if src_ip == "192.168.1.11":
                        dst_ip = "192.168.2.11"
                    elif src_ip == "192.168.2.11":
                        dst_ip = "192.168.1.11"
                    else:
                        raise ValueError("Invalid IP address")
                    
                    content = Ipv4Pkt(src_ip, dst_ip, payload="Hello, VnfApp!")
                    message = OMessage(f"{self.scheduler.now}", f"{self.name}", "AimVnf", content, f"{self.name}{self.pkt_count}")
                    self.send_msg(message, gate)
                    self.logger.log(event="-", time=self.scheduler.now, from_node=self.name, to_node="AimVnf", pkt_type="Hello", 
                                    pkt_size=len(message), pkt_id=message.id)
                    
                    self.pkt_count += 1
                    self.clocktime.set_tick_interval(random.randint(1, 5)*u.min)
        elif gate.name == "lowerLayerIn":
            self.logger.log(event="+", time=self.scheduler.now, from_node=msg.sender, to_node=self.name, pkt_type="Hello", 
                            pkt_size=len(msg), pkt_id=msg.id, pkt_delay=self.scheduler.now - float(msg.timestamp))

class VnfAppSrv4(SimpleApp):
    def __init__(self, name: str, service_model:str="Stabled"):
        """ VNF 的应用层模型模拟 SFC 上数据处理过程
        
        Args:
            name (str): 模块名称
            service_model (str, optional): 服务模型 ("Stabled"/"Poisson"). Defaults to "Stabled".
        """
        super().__init__(name)
        
        self.process_rate:float = 1
        """ VNF的消息处理速率 (数据包/ms)"""
        
        self.performance_record:list[float] = []
        """节点的业务性能记录 (当该节点为SFC的末端时记录到达数据包的总经历时延)"""
        
        self.service_model = service_model
        """服务模型 ("Stabled"/"Poisson")"""
        
        self.msg_pool:list[OMessage] = []
        """用于记录已经接收到的业务数据包, 用于过滤重复数据包"""
    
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
    
    def req_and_process(self,msg:"OMessage"):
        """
        请求计算资源并处理数据包 (耗时过程)

        Args:
            msg (OMessage): 待处理数据包

        Yields:
            req: 计算资源请求对象
            time: 计算资源请求时间
        """
                    
        self.logger.info(f"{self.scheduler.now}: Module '{self.name}' get packet and wait for processing resource *******************************")
        
        request = self.req_processor.request()
        self.req2msg[request] = msg
        
        with request as req:
            yield req
            
            # VNF 得到计算资源开始处理数据包 -----------------------------------
            
            if self.service_model == "Stabled":
                processing_delay = 1 / self.process_rate  # 节点处理延迟
                yield self.scheduler.timeout(processing_delay)  
            elif self.service_model == "Poisson":
                yield self.scheduler.timeout(random.expovariate(self.process_rate))
            else:
                raise ValueError(f"Unsupported service model: {self.service_model}")
            
            # VNF 处理数据包处理完成 --------------------------------------------
    
            srvs4pkt:Srv4Pkt = msg.content
            srvs4pkt.segment_left -= 1                                       # 更新地址指示
            srvs4pkt.dst_ip = srvs4pkt.segment_list[srvs4pkt.segment_left]   # 提取目的地址
            
            content = srvs4pkt
            message = OMessage(timestamp=f"{msg.timestamp}", 
                               sender=f"{msg.sender}", 
                               receiver=f"{msg.receiver}", 
                               content=content, 
                               id=f"{msg.id}",
                               ttl=f"{msg.ttl}")
            
            for gate in self.gates:
                if gate.name == "lowerLayerOut":
                    self.send_msg(message, gate)
                    
                    self.logger.log(event="-", time=self.scheduler.now, from_node=msg.sender, to_node=msg.receiver, pkt_type="UeAppSrv4Pkt", 
                                    pkt_size=len(msg), pkt_id=msg.id, src_addr=srvs4pkt.src_ip, dst_addr=srvs4pkt.dst_ip, 
                                    pkt_delay=self.scheduler.now - float(msg.timestamp))
            
            
    
    def recv_msg(self, msg:"OMessage", gate:"OGate"):
        if msg.sender == f"{self.name}Timer":
            # VNF 不应自身产生数据，当作异常处理
            self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' should not receive timer message from {msg.sender} to make it start sending data")
            
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
                    
                    self.logger.log(event="r", time=self.scheduler.now, from_node=msg.sender, to_node=msg.receiver, pkt_type="VnfAppSrv4Pkt", 
                                    pkt_size=len(msg), pkt_id=msg.id, src_addr=srvs4pkt.src_ip, dst_addr=srvs4pkt.dst_ip, 
                                    pkt_delay=self.scheduler.now - float(msg.timestamp))
                    
                else:
                    # 中间分段，需要中继处理
                    self.logger.log(event="+", time=self.scheduler.now, from_node=msg.sender, to_node=msg.receiver, pkt_type="VnfAppSrv4Pkt", 
                                    pkt_size=len(msg), pkt_id=msg.id, src_addr=srvs4pkt.src_ip, dst_addr=srvs4pkt.dst_ip, 
                                    pkt_delay=self.scheduler.now - float(msg.timestamp))
                    
                    self.scheduler.process(self.req_and_process(msg))
                        
            else:
                # 数据包不是发给自己的，大概率是上一跳路由发生了错误，丢弃
                self.logger.warning(f"{self.scheduler.now}: Module '{self.name}' get packet from {msg.sender} with invalid destination IP address {srvs4pkt.dst_ip}")
                    