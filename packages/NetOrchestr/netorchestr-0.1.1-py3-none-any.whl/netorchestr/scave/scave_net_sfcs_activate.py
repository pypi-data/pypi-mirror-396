#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-

'''
scave_net_sfcs_activate.py
==========================

.. module:: scave_net_sfcs_activate
  :platform: Windows
  :synopsis: 该模块用于解析 NetOrchestra 仿真器输出的 MANO 部署过程的日志数据，并绘制网络 SFC 激活数量随时间变化的图表.

.. moduleauthor:: WangXi

简介
----

该模块实现了从 NetOrchestra 仿真器输出的 MANO 数据中解析网络服务功能链 SFC 在网激活数量的功能, 主要用于网络编排和虚拟网络功能 VNF 部署的研究与分析中. 
它提供了以下特性:

- 解析 CSV 文件以获取 SFC 激活数据.
- 使用 matplotlib 库绘制 SFC 激活数量随时间变化的图表.
- 支持多种绘图样式（如线条样式、标记样式等）.

版本
----

- 版本 1.0 (2025/11/19): 初始版本

'''

import os
import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
from astropy import units as u
from astropy.time import Time
import matplotlib.dates as mdates

def main():

    # region 定义风格
    from netorchestr.scave import STYLE_DRAW
    color_Bar = STYLE_DRAW.COLOUR_BAR_4
    linestyle_Bar = STYLE_DRAW.LINESTYLE_BAR
    marker_Bar = STYLE_DRAW.MARKER_BAR
    # endregion

    # region 获取数据
    from netorchestr.scave import DATA_GROUP
    init_time = DATA_GROUP.TIME_SIM_START
    data = DATA_GROUP.DATA_ALL_ALGORITHMS

    def __get_array_from_file(filepath:str):
        data = pd.read_csv(filepath)
        dataFrame = np.array(copy.deepcopy(data[['Time','Vnffgs']]))
        dataFrame_dict = {}
        for i in range(len(dataFrame)):
            if i == 0:
                dataFrame_dict[init_time + (4.0 * u.hour)] = 0
                continue
            
            time_ms = dataFrame[i][0] * u.ms
            time_real = init_time + time_ms
            vnffgs_count = len(np.array(literal_eval(dataFrame[i][1])))
            
            dataFrame_dict[time_real] = vnffgs_count
        
        return dataFrame_dict

    for algo in data.keys():
        data[algo]['data'] = __get_array_from_file(data[algo]['filepath'])

    # region 开始绘图

    title ='Network SFC Activation Number'
    xlabel='Time'
    ylabel='SFC activated in network'

    fig = plt.figure(figsize=(10, 3))
    ax = plt.axes()
    ax.set(xlabel=xlabel,ylabel=ylabel)

    for i,algo in enumerate(data.keys()):
        time_astropy:list[Time] = list(data[algo]['data'].keys())
        time_datetime = [t.to_datetime() for t in time_astropy]
        vnffgs_count = list(data[algo]['data'].values())
        
        ax.plot(time_datetime,
                vnffgs_count,
                label=str(algo),
                color=color_Bar[i %len(color_Bar)],
                linestyle=linestyle_Bar[i %len(linestyle_Bar)],
                marker=marker_Bar[i %len(marker_Bar)],
                markersize=2,
                markevery=10)

    ax.grid(True, linestyle='--', alpha=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.legend()

    if not os.path.exists('fig'):
        os.makedirs('fig')

    fig.savefig('fig/'+title.replace(' ','_')+'.svg',format='svg',dpi=150)
    fig.savefig('fig/'+title.replace(' ','_')+'.pdf', bbox_inches='tight', pad_inches=0.5)


if __name__ == '__main__':
    main()
    
