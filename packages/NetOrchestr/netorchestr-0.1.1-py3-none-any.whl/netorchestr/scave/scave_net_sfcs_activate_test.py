#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-

'''
scave_net_sfcs_activate_test.py
===============================

.. module:: scave_net_sfcs_activate_test
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
- **新增**: 支持通过开关控制绘制方式（单图/子图），并统一子图坐标轴。

版本
----

- 版本 2.0 (2025/11/19): 增加了子图绘制功能及坐标轴统一控制。
'''

import os
import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
from astropy import units as u
import matplotlib.dates as mdates

def main():
    # ==============================================================================
    # 设置为 True 以使用子图绘制，设置为 False 则在同一图中绘制所有曲线
    use_subplots = True 
    # ==============================================================================

    # region 定义风格
    from netorchestr.scave import STYLE_DRAW
    color_Bar = STYLE_DRAW.COLOUR_BAR_1
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

    # 加载所有数据
    for algo in data.keys():
        data[algo]['data'] = __get_array_from_file(data[algo]['filepath'])
        # 将时间转换为 datetime 并存储，方便后续处理
        data[algo]['datetime'] = [t.to_datetime() for t in data[algo]['data'].keys()]
        data[algo]['counts'] = list(data[algo]['data'].values())

    # endregion

    # region 计算全局坐标轴范围 (用于统一子图)
    all_datetimes = []
    all_counts = []
    for algo_data in data.values():
        all_datetimes.extend(algo_data['datetime'])
        all_counts.extend(algo_data['counts'])

    # 统一时间范围
    global_x_min, global_x_max = min(all_datetimes), max(all_datetimes)
    # 统一数值范围，并留出一些边距使图表更美观
    global_y_min, global_y_max = 0, max(all_counts) * 1.1
    # endregion

    # region 开始绘图
    title ='Network SFC Activation Number'
    xlabel='Time'
    ylabel='SFC activated in network'

    if use_subplots:
        # --- 子图模式 ---
        num_algos = len(data.keys())
        # 创建一个包含 num_algos 个子图的画布，垂直排列
        fig, axes = plt.subplots(nrows=num_algos, ncols=1, figsize=(12, 3 * num_algos), sharex=True)
        fig.suptitle(title, y=0.98) # 添加一个总标题

        for i, (algo, ax) in enumerate(zip(data.keys(), axes)):
            ax.plot(data[algo]['datetime'],
                    data[algo]['counts'],
                    label=str(algo),
                    color=color_Bar[i % len(color_Bar)],
                    linestyle=linestyle_Bar[i % len(linestyle_Bar)],
                    marker=marker_Bar[i % len(marker_Bar)],
                    markersize=4,
                    markevery=10,
                    linewidth=2)

            # --- 核心：统一所有子图的Y轴范围 ---
            ax.set_ylim(global_y_min, global_y_max)
            
            ax.set_ylabel(ylabel)
            ax.legend(loc='upper left')
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        # 只在最下面的子图显示X轴标签
        axes[-1].set_xlabel(xlabel)
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # 调整子图间距，防止标题和标签重叠
        plt.tight_layout(rect=[0, 0, 1, 0.96])

    else:
        # --- 单图模式 ---
        fig = plt.figure(figsize=(12, 7))
        ax = plt.axes()
        ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        for i, algo in enumerate(data.keys()):
            ax.plot(data[algo]['datetime'],
                    data[algo]['counts'],
                    label=str(algo),
                    color=color_Bar[i % len(color_Bar)],
                    linestyle=linestyle_Bar[i % len(linestyle_Bar)],
                    marker=marker_Bar[i % len(marker_Bar)],
                    markersize=4,
                    markevery=20,
                    linewidth=2)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        # 将图例放在图外，避免遮挡曲线
        ax.legend(ncol=2, bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.tight_layout()

    # endregion

    # 保存图片
    if not os.path.exists('fig'):
        os.makedirs('fig')

    # 根据模式保存不同名称的图片，方便区分
    if use_subplots:
        fig.savefig('fig/' + title.replace(' ', '_') + '_subplots.svg', format='svg', dpi=300, bbox_inches='tight')
        fig.savefig('fig/' + title.replace(' ', '_') + '_subplots.pdf', bbox_inches='tight')
    else:
        fig.savefig('fig/' + title.replace(' ', '_') + '_single_plot.svg', format='svg', dpi=300, bbox_inches='tight')
        fig.savefig('fig/' + title.replace(' ', '_') + '_single_plot.pdf', bbox_inches='tight')

    # plt.show()
    
    

if __name__ == '__main__':
    main()
