
import os
import time
import socket
import logging
from dataclasses import dataclass

@dataclass
class OLogItem:
    """仿真记录项"""
    event: str        # 事件类型
    time: float       # 事件发生时间
    from_node: str    # 数据包的发出节点
    to_node: str      # 数据包的接收节点
    pkt_type: str     # 数据包的类型
    pkt_size: int     # 数据包的大小
    flags: str        # 事件的标志
    fid: int          # 连接的ID号
    src_addr: str     # 数据包源地址
    dst_addr: str     # 数据包目的地址
    seq_num: int      # 数据包的序列号
    pkt_id: str       # 数据包的ID号
    pkt_delay: float  # 数据包的延迟时间

class OLogger:
    """仿真事件记录器"""
    def __init__(self, 
                 name,
                 sim_id:str = "", 
                 seed_id:int = 0,
                 work_dir:str = None):
        
        self.name_net = name.split('_')[0]
        self.sim_id = sim_id
        self.seed_id = seed_id
        self.work_dir = work_dir
        
        if self.sim_id == "":
            self.sim_id = OLogger.get_run_id()
            
        print(f"INFO: 当前仿真 ID {self.sim_id}")
        
        # 在工作目录下创建日志目录
        if self.work_dir is None:
            self.work_dir = os.getcwd()
            
        self.log_dir = os.path.join(self.work_dir, self.name_net+f'_{self.sim_id}_{self.seed_id}')
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        self.logger = logging.getLogger(f"{self.name_net}_trace")
        self.logger_file_handler = logging.FileHandler(os.path.join(self.log_dir, f"{self.name_net}_trace.log"), mode='w', encoding='utf-8')
        self.logger_file_handler.setLevel(logging.INFO)
        logger_file_formatter = logging.Formatter('%(message)s')
        self.logger_file_handler.setFormatter(logger_file_formatter)
        self.logger.addHandler(self.logger_file_handler)
        self.logger.setLevel(logging.INFO)
        
        self.debug_logger = logging.getLogger(f"{self.name_net}_debug")
        self.debug_file_handler = logging.FileHandler(os.path.join(self.log_dir, f"{self.name_net}_debug.log"), mode='w', encoding='utf-8')
        self.debug_file_handler.setLevel(logging.DEBUG)
        debug_file_formatter = logging.Formatter('%(message)s')
        self.debug_file_handler.setFormatter(debug_file_formatter)
        self.debug_logger.addHandler(self.debug_file_handler)
        self.debug_logger.setLevel(logging.DEBUG)
        
        
    def log(self, event="*", time="*", from_node="*", to_node="*", pkt_type="*", pkt_size="*", 
            flags="*", fid="*", src_addr="*", dst_addr="*", seq_num="*", pkt_id="*", pkt_delay="*"):
        """记录事件"""
        
        self.logger.info(f"{event} {time} {from_node} {to_node} {pkt_type} {pkt_size} {flags} {fid} {src_addr} {dst_addr} {seq_num} {pkt_id} {pkt_delay}")
        
        
    def warning(self, message):
        """记录警告信息"""
        self.debug_logger.warning(message)
    
    def error(self, message):
        """记录错误信息"""
        self.debug_logger.error(message)
    
    def debug(self, message):
        """记录调试信息"""
        self.debug_logger.debug(message)
    
    def info(self, message):
        """记录一般信息"""
        self.debug_logger.info(message)
    
    def set_console_level(self, level):
        """设置调式日志级别"""
        self.debug_file_handler.setLevel(level)
        
    def extract_log_items(self):
        """从日志文件中提取记录项"""
        log_items = []
        with open(self.logger_file_handler.baseFilename, 'r', encoding='utf-8') as f:
            for line in f:
                items = line.strip().split()
                if len(items) == 13:
                    log_item = OLogItem(event=items[0], time=items[1], 
                                       from_node=items[2], to_node=items[3], 
                                       pkt_type=items[4], pkt_size=int(items[5]), 
                                       flags=items[6], fid=items[7], 
                                       src_addr=items[8], dst_addr=items[9], 
                                       seq_num=items[10], pkt_id=items[11], 
                                       pkt_delay=items[12])
                    log_items.append(log_item)
        return log_items
    
    @staticmethod
    def get_time_stamp():
        ct = time.time()
        local_time = time.localtime(ct)
        data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        data_secs = (ct - int(ct)) * 1000
        time_stamp = "%s.%03d" % (data_head, data_secs)
        stamp = ("".join(time_stamp.split()[0].split("-"))+"".join(time_stamp.split()[1].split(":"))).replace('.', '')
        return stamp

    @staticmethod
    def get_run_id() -> str:
        run_time = OLogger.get_time_stamp()
        host_name = socket.gethostname()
        run_id = f'{host_name}_{run_time}'
        return run_id
    


