

import numpy as np
from astropy import units as u
from astropy.time import Time
from netorchestr.envir.mobility import MobilityDynamic

class Trajectory:
    def __init__(self, name:str, avg_speed:float, **kwargs):
        """轨迹规划

        Args:
            name (str): 轨迹名称
            avg_speed (float): 平均移速 (m/s)
        """
        self.name = name
        
        self.avg_speed = avg_speed
        """平均移速 (m/s)"""
        
        self.waypoints = []
        """轨迹点列表 [(纬度, 经度, 高度, 累计时间)]"""

    def add_straight(self, start:tuple, end:tuple):
        """添加两点之间的直线轨迹

        根据起始点和终止点坐标,计算平台的直线路径,
        轨迹点数量和运动时间由平均速度自动确定,距离计算考虑了地球曲率近似。

        Args:
            start (tuple): 起点坐标,格式为 (经度, 纬度, 高度km)
                        示例: (120.0, 30.0, 0) 表示东经120度北纬30度,海拔0km
            end (tuple): 终点坐标,格式为 (经度, 纬度, 高度km)
                        示例: (120.1, 30.1, 1) 表示东经120.1度北纬30.1度,海拔1km

        Returns:
            None: 轨迹点会添加到self.waypoints列表中,格式为 (纬度, 经度, 高度, 累计时间)

        Notes:
            1. 距离计算采用近似方法: 111320米≈1纬度,经度距离按cos(纬度)缩放
            2. 高度差直接参与三维距离计算
            3. 默认生成10个均匀分布的轨迹点
            4. 时间累计计算确保多段轨迹连续

        Example:
            >>> otraj = OTraj(avg_speed=10.0)  # 10米/秒
            >>> otraj.add_straight((120.0, 30.0, 0), (120.0, 30.1, 1))
            # 生成从30°N到30.1°N的直线路径,经度保持120°E,爬升至1km高度
            # 经历时间约为1113.2秒(距离11132米/速度10m/s)
        """
        # 解构起点和终点坐标
        lon1, lat1, alt1 = start  # 起点经度/纬度/高度
        lon2, lat2, alt2 = end    # 终点经度/纬度/高度
        
        # 计算三维距离(考虑地球曲率近似)
        # 纬度距离: 1度 ≈ 111320米
        lat_dist = (lat2 - lat1) * 111320  
        # 经度距离: 1度 ≈ 111320*cos(纬度)米 
        lon_dist = (lon2 - lon1) * 111320 * np.cos(np.radians((lat1 + lat2)/2))
        # 高度差直接取差值
        alt_dist = alt2 - alt1  
        
        # 计算总距离和所需时间
        dist = np.sqrt(lat_dist**2 + lon_dist**2 + alt_dist**2)  # 三维欧氏距离
        duration = dist / self.avg_speed  # 移动时间(秒)

        # 生成插值点(默认10个轨迹点)
        t = np.linspace(0, duration, 10)  # 时间轴均匀分布
        lat = np.linspace(lat1, lat2, len(t))  # 纬度线性插值
        lon = np.linspace(lon1, lon2, len(t))  # 经度线性插值
        alt = np.linspace(alt1, alt2, len(t))  # 高度线性插值
        
        # 计算时间基准(累计之前所有路段时间)
        base_time = self.waypoints[-1][3] if self.waypoints else 0
        
        # 添加轨迹点到列表
        for ti, la, lo, al in zip(t, lat, lon, alt):
            self.waypoints.append((
                la,      # 纬度(度)
                lo,      # 经度(度) 
                al,      # 高度km
                ti + base_time  # 累计时间(秒)
            ))
    
    def add_circle(self, center, radius, loops=1):
        """添加圆形移动轨迹
        
        根据中心点坐标和半径生成圆形移动路径,支持多圈绕行,
        自动计算移动时间并保持恒定速度。

        Args:
            center (tuple): 圆心坐标 (经度, 纬度, 高度km)
                            示例: (120.0, 30.0, 1) 表示北纬30度东经120度,海拔1km
            radius (float): 圆半径(单位:米)
                            示例: 50 表示50米半径的圆形
            loops (int):    绕行圈数,默认为1
                            示例: 2 表示绕行两圈

        Returns:
            None: 轨迹点会添加到self.waypoints列表中,格式为 (纬度, 经度, 高度, 累计时间)

        Notes:
            1. 通过极坐标方程生成圆形路径点
            2. 经纬度转换考虑地球曲率(111320米/度)
            3. 经度距离按cos(纬度)缩放
            4. 自动计算移动时间保持恒定速度
            纬度 = 中心纬度 + (radius/111320) * cos(θ)
            经度 = 中心经度 + (radius/(111320*cos(纬度))) * sin(θ)
            其中θ为极角

        Example:
            >>> otraj = OTraj(avg_speed=5.0)  # 5米/秒
            >>> otraj.add_circle((30.0, 120.0, 1), 50, 2)
            # 生成圆心经纬度为30°N,120°E, 海拔1km高度, 半径50米的圆形轨迹, 绕行2圈
            # 总距离 = 2 * π * 50 * 2 ≈ 628.3米
            # 移动时间 ≈ 628.3/5 ≈ 125.66秒
        """
        # 解构中心点坐标
        lon0, lat0, alt0 = center  # 圆心经度/纬度/高度
        
        # 计算圆形周长和总移动时间
        circumference = 2 * np.pi * radius  # 单圈周长
        duration = circumference * loops / self.avg_speed  # 总移动时间
        
        # 生成极角参数(支持多圈绕行)
        theta = np.linspace(0, 2*np.pi*loops, 1000)  # 默认50个轨迹点/圈
        t = np.linspace(0, duration, len(theta))   # 时间轴
        
        # 地球曲率常数(米/度)
        meters_per_degree = 111320
        
        # 生成圆形轨迹点
        for angle, time in zip(theta, t):
            # 纬度计算(直接使用弧度值)
            lat = lat0 + (radius / meters_per_degree) * np.cos(angle)
            
            # 经度计算(考虑纬度缩放)
            lon = lon0 + (radius / (meters_per_degree * np.cos(np.radians(lat0)))) * np.sin(angle)
            
            # 添加轨迹点(时间累计计算)
            self.waypoints.append((
                lat,  # 纬度(度)
                lon,  # 经度(度)
                alt0,  # 保持固定高度(km)
                time + (self.waypoints[-1][3] if self.waypoints else 0)  # 累计时间(秒)
            ))
            
    def add_figure8(self, center, size, loops=1):
        """添加八字移动轨迹(双纽线)
        
        生成标准的八字形移动路径(数学上称为双纽线),支持多圈绕行,
        自动根据平均速度计算移动时间。

        Args:
            center (tuple): 轨迹中心点 (经度, 纬度, 高度km)
                        示例: (120.0, 30.0, 1) 表示北纬30度东经120度,海拔1km
            size (float):   轨迹尺寸(单位:米),控制整体大小
                        示例: 50 表示宽度约50米的八字轨迹
            loops (int):    绕行圈数,默认为1
                        示例: 2 表示绕行两个完整的八字

        Returns:
            None: 轨迹点会添加到self.waypoints列表中,格式为 (纬度, 经度, 高度, 累计时间)

        Notes:
            1. 使用双纽线参数方程:
            x = a * sinθ
            y = a * sinθ * cosθ
            2. 周长近似公式:L ≈ 5.244 * size
            3. 经纬度转换:
            纬度偏移 = (a * sinθ) / 111320
            经度偏移 = (a * sinθ * cosθ) / (111320 * cos(纬度))

            1. 每圈默认生成50个轨迹点
            2. 自动计算总移动时间(总距离/平均速度)
            3. 经度距离补偿了纬度缩放因子

        Example:
            >>> otraj = OTraj(avg_speed=2.0)  # 2米/秒
            >>> otraj.add_figure8((120.0, 30.0, 1), 30, 3)
            # 生成高度1km,尺寸30米的八字轨迹,绕行3圈
            # 总距离 ≈ 5.244 * 30 * 3 ≈ 472米
            # 移动时间 ≈ 472/2 ≈ 236秒
        """
        # 解构中心点坐标
        lon0, lat0, alt0 = center
        
        # 1. 计算轨迹总长度和移动时间
        single_loop_length = 5.244 * size  # 双纽线周长近似值
        total_length = single_loop_length * loops
        duration = total_length / self.avg_speed
        
        # 2. 生成参数化角度(支持多圈)
        theta = np.linspace(0, 2 * np.pi * loops, 1000 * loops)  # 50点/圈
        t = np.linspace(0, duration, len(theta))  # 时间轴
        
        # 3. 双纽线参数计算
        a = size / 111320  # 将米转换为纬度偏移量
        
        # 4. 生成轨迹点
        base_time = self.waypoints[-1][3] if self.waypoints else 0  # 获取当前最后时间
        for angle, time in zip(theta, t):
            # 纬度计算(正弦分量)
            lat = lat0 + a * np.sin(angle)
            
            # 经度计算(正弦*余弦分量,考虑纬度缩放)
            lon = lon0 + (a * np.sin(angle) * np.cos(angle)) / np.cos(np.radians(lat0))
            
            # 添加轨迹点(固定高度,累计时间)
            self.waypoints.append((
                lat,    # 纬度(度)
                lon,    # 经度(度)
                alt0,   # 高度(km)
                base_time + time  # 累计时间(秒)
            ))
    
    def add_random_in_circle(self, center, radius, anchor_number=10):
        """在圆形区域内添加随机路径

        在指定的圆形区域内随机生成多个锚点，通过依次连接锚点形成随机移动路径，
        相邻锚点之间采用直线轨迹，轨迹点生成和时间计算逻辑与`add_straight`保持一致。

        Args:
            center (tuple): 圆心坐标 (经度, 纬度, 高度km)
                            示例: (120.0, 30.0, 1) 表示东经120度北纬30度,海拔1km
            radius (float): 圆形区域半径(单位:米)
                            示例: 100 表示以圆心为中心、100米为半径的圆形区域
            anchor_number (int): 随机锚点数量,默认为10, 锚点数越多, 总路径越长
                            示例: 5 表示在圆形区域内生成5个随机锚点

        Returns:
            None: 轨迹点会添加到self.waypoints列表中,格式为 (纬度, 经度, 高度, 累计时间)

        Notes:
            1. 锚点生成逻辑: 在圆形区域内按极坐标随机分布,半径0~radius随机,角度0~2π随机
            2. 路径连接方式: 从当前轨迹终点开始,依次直线连接所有锚点
            3. 高度处理: 所有锚点高度与圆心高度保持一致
            4. 轨迹点生成: 每段直线轨迹的点数量与`add_straight`相同(默认10个/段)
            5. 时间累计: 保持与已有轨迹的时间连续性,计算方式同`add_straight`

        Example:
            >>> traj = Trajectory("随机路径", avg_speed=2.0)
            >>> traj.add_random_in_circle((120.0, 30.0, 50), 80, 8)
            # 生成以(120.0°E,30.0°N,50m)为中心、80米半径的圆形区域内的随机路径
            # 包含8个随机锚点,平均速度2米/秒
            # 路径从初始位置(圆心)开始,依次连接8个锚点
        """
        if anchor_number < 1:
            raise ValueError("锚点数量anchor_number必须至少为1")
        
        # 解析圆心坐标
        lon0, lat0, alt0 = center
        meters_per_degree = 111320  # 1度纬度对应的米数
        lat0_rad = np.radians(lat0)
        cos_lat0 = np.cos(lat0_rad)  # 用于经度偏移计算的纬度缩放因子

        # 生成随机锚点(极坐标随机分布)
        np.random.seed(None)  # 不固定随机种子
        r = np.random.uniform(0, radius, anchor_number)  # 随机半径(0~radius)
        theta = np.random.uniform(0, 2 * np.pi, anchor_number)  # 随机角度(0~2π)
        anchors = []
        
        for ri, thetai in zip(r, theta):
            # 计算纬度偏移(度): 米 -> 纬度度
            delta_lat = (ri * np.cos(thetai)) / meters_per_degree
            # 计算经度偏移(度): 米 -> 经度度(考虑纬度缩放)
            delta_lon = (ri * np.sin(thetai)) / (meters_per_degree * cos_lat0)
            # 构建锚点坐标(经度, 纬度, 高度)
            anchor = (lon0 + delta_lon, lat0 + delta_lat, alt0)
            anchors.append(anchor)

        # 确定路径起始点
        if self.waypoints:
            # 从当前轨迹的最后一个点开始
            last_wp = self.waypoints[-1]
            start = (last_wp[1], last_wp[0], last_wp[2])  # 转换为(经度,纬度,高度)格式
        else:
            # 轨迹为空时从圆心开始
            start = center

        # 依次连接所有锚点(调用add_straight实现直线轨迹)
        for anchor in anchors:
            self.add_straight(start, anchor)
            start = anchor  # 更新起点为当前锚点
    
    
    def query_position(self, time):
        """查询在指定时刻的预期位置
        
        通过线性插值计算任意时刻的经纬度和高度，
        当查询时间超过总时长时返回最后一个轨迹点位置。

        Args:
            time (float): 查询时间（单位：秒）
                        示例: 25.3 表示移动开始后25.3秒时的位置

        Returns:
            tuple: 三维坐标 (纬度, 经度, 高度km)
                纬度/经度单位：度
                高度单位: km

        Notes:
            1. 提取所有轨迹点的时间序列和坐标序列
            2. 使用numpy的interp函数进行线性插值
            3. 对纬度、经度、高度分别进行插值计算
            4. 超时情况返回最后一个轨迹点

            边界处理:
                - 时间<0: 返回起点坐标
                - 时间>总时长: 返回终点坐标
                - 空轨迹点列表: 返回(0,0,0)

            计算复杂度:
                O(n) 其中n为轨迹点数量

        Example:
            >>> otraj = OTrajTrajectory(avg_speed=5.0)
            >>> otraj.add_straight((30.0,120.0,0), (30.1,120.0,100))
            >>> otraj.query_position(10.0)
            (30.05, 120.0, 50.0)  # 移动中途点
        """
        # 边界条件检查
        if not self.waypoints:
            return (0.0, 0.0, 0.0)  # 空轨迹点列表返回原点
        
        # 提取时间序列和各坐标轴数据
        times = np.array([wp[3] for wp in self.waypoints])  # 所有轨迹点的时间戳
        lats = np.array([wp[0] for wp in self.waypoints])   # 纬度序列
        lons = np.array([wp[1] for wp in self.waypoints])   # 经度序列
        alts = np.array([wp[2] for wp in self.waypoints])   # 高度序列
        
        # 处理超时情况
        if time <= times[0]:
            return self.waypoints[0][:3]  # 返回起点
        if time >= times[-1]:
            return self.waypoints[-1][:3]  # 返回终点
        
        # 三维线性插值
        lat = np.interp(time, times, lats)  # 纬度插值
        lon = np.interp(time, times, lons)  # 经度插值
        alt = np.interp(time, times, alts)  # 高度插值
        
        return (lat, lon, alt)


class MobilityTraj(MobilityDynamic):
    def __init__(self, name:str, init_time:Time, init_gps:list[float], markcolor:str='yellow'):
        """运动轨迹类运行模型
        
        Args:
            name (str): 运动轨迹名称
            init_time (Time): 初始时间
            init_gps (list[float]): 初始GPS坐标 [经度, 纬度, 高度km]
            markcolor (str): 标记颜色, 默认为'yellow'
            
        Note:
            运动轨迹类运行模型, 继承自MobilityDynamic类, 实现了运动轨迹的运行模型。
            运动轨迹类中包含一个Trajectory对象, 用于存储运动轨迹信息, 包括轨迹点、平均速度等。
            运动轨迹类中包含一个update_current_gps方法, 用于根据当前时间更新当前GPS坐标, 并缓存坐标信息。
        """
        
        super().__init__(name, init_time, init_gps, markcolor)
        
        self.speed_avg = None
        """移动速度, 单位km/s"""
        
        self.time_start:Time = None
        """开始移动时间"""
        
        self.time_end:Time = None
        """结束移动时间"""
        
        self.trajectory:Trajectory = None
        """轨迹规划对象"""
        
    def set_trajectory(self, trajectory:Trajectory, time_start:Time) -> None:
        """设置运动轨迹, 并设置开始运动时间

        Args:
        
        Note:
            轨迹停止时间根据最后一个航线点设置获取
            
        """
        self.trajectory = trajectory
        self.time_start = time_start
        self.time_end = self.time_start + self.trajectory.waypoints[-1][3] * u.s
        self.speed_avg = (self.trajectory.avg_speed * u.m / u.s).to(u.km / u.s).value

    def update_current_gps(self, time:u.quantity):
        """更新当前GPS坐标
        
        通过当前时间更新当前GPS坐标, 并缓存坐标信息。
        
        Args:
            time (u.quantity): 仿真开始后经历的时长
        
        Returns:
            list: 当前GPS坐标 [经度, 纬度, 高度km]
            
            bool: 是否是从缓存中获取的坐标信息
        """
        self.current_time = self.init_time + np.around(time.to(u.ms))
        
        # 检查缓存中是否有当前时间的坐标
        if self.current_time in self.cache_gps:
            self.current_gps = self.cache_gps[self.current_time]
            return self.current_gps, True

        # 检查是否已规划航线
        if self.trajectory is None:
            return self.current_gps, True

        # 当前时间早于出发时间，返回出发点
        if self.current_time < self.time_start:
            self.current_gps = [self.trajectory.waypoints[0][1],self.trajectory.waypoints[0][0],self.trajectory.waypoints[0][2]]
            self.cache_gps[self.current_time] = self.current_gps
            return self.current_gps, True

        # 当前时间超过轨迹结束时间，返回目的地
        if self.current_time >= self.time_end:
            self.current_gps = [self.trajectory.waypoints[-1][1],self.trajectory.waypoints[-1][0],self.trajectory.waypoints[-1][2]]
            self.cache_gps[self.current_time] = self.current_gps
            return self.current_gps, True
        
        delta_time_s = (self.current_time - self.time_start).to(u.s).value  # 当前时间与起飞时间差值(秒)
        current_lat, current_lon, current_alt = self.trajectory.query_position(delta_time_s)  # 查询当前位置

        self.current_gps = [current_lon, current_lat, current_alt/1000.0]
        
        # 缓存当前时间坐标
        self.cache_gps[self.current_time] = self.current_gps
            
        return self.current_gps, False
