#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-

'''
scave_net_sys_perf_sfc_length.py
================================

.. module:: scave_net_sys_perf_sfc_length
  :platform: Windows
  :synopsis: 该模块用于解析 NetOrchestra 仿真器输出的 MANO 求解器输出的日志数据, 并绘制不同SFC长度下系统部署时的各求解器的性能情况.

.. moduleauthor:: WangXi

简介
----

该模块实现了从 NetOrchestra 仿真器输出的 MANO 数据中解析不同SFC长度下系统部署时的各求解器的性能情况, 主要用于网络编排和虚拟网络功能 VNF 部署的研究与分析中. 
它提供了以下特性:

- 解析 CSV 文件以获取系统运行过程日志.
- 使用 matplotlib 库绘制求解器性能随时间变化的图表.
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
from astropy import units as u
import matplotlib.ticker as ticker

def main():

    # region 定义风格
    from netorchestr.scave import STYLE_DRAW
    color_Bar = STYLE_DRAW.COLOUR_BAR_4
    linestyle_Bar = STYLE_DRAW.LINESTYLE_BAR
    marker_Bar = STYLE_DRAW.MARKER_BAR

    # region 获取数据
    from netorchestr.scave import DATA_GROUP
    init_time = DATA_GROUP.TIME_SIM_START
    data = DATA_GROUP.DATA_ENV_SFC_LENGTH

    def __get_array_from_file(filepath:str, watch_item:str):
        data = pd.read_csv(filepath)
        dataFrame = np.array(copy.deepcopy(data[['Time',watch_item]]))
        dataFrame_dict = {}
        for i in range(len(dataFrame)):
            if i == 0:
                dataFrame_dict[init_time + (4.0 * u.hour)] = 0
                continue
            
            time_ms = dataFrame[i][0] * u.ms
            time_real = init_time + time_ms
            
            # 计算系统收益支出比
            watch_value = float(dataFrame[i][1])
            
            dataFrame_dict[time_real] = watch_value
        
        return dataFrame_dict

    # region 开始绘图

    title ='Solver Performance under Different SFC Lengths'

    wfig=5
    hfig=3
    wspace=0.2
    hspace=0.3
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=((wfig+wspace)*3, (hfig+hspace)*1), sharex=False)
    # fig.suptitle(title, y=1.2)
    fig.subplots_adjust(wspace=wspace,hspace=hspace)


    algo_list = list(dict.fromkeys([algo_env_index.split('_')[0] for algo_env_index in data.keys()]))
    print(algo_list)
    watch_items = {
        "SysRev":"System Revenue",
        "SysCost":"System Cost",
        "SysRevCostRatio":"System Revenue Cost Ratio",
    }
    sfc_length_list = np.arange(3, 13, 2)  # 结果：[3, 5, 7, 9, 11]

    for algo_env_index in data.keys():
        for item in list(watch_items.keys()):
            data[algo_env_index][item] = __get_array_from_file(data[algo_env_index]['filepath'], watch_item=item)

    bar_width = 0.3                                                  # bar宽度
    bar_per_group = int(len(data.keys())/len(sfc_length_list))       # 每组bar数量
    group_num = len(sfc_length_list)                                 # 总分组数
    intra_group_gap = 0.01                                           # 组内间距
    inter_group_gap = 0.5                                            # 组间间距

    index_array = []
    for group_idx in range(group_num):
        # 计算当前组的基准位置
        group_base = group_idx * (bar_per_group * (bar_width + intra_group_gap) + inter_group_gap)
        # 计算组内每个bar的索引
        for bar_idx in range(bar_per_group):
            bar_pos = group_base + bar_idx * (bar_width + intra_group_gap)
            index_array.append(bar_pos)
            
    index_2d = []
    for bar_idx in range(bar_per_group):
        bar_positions = index_array[bar_idx::bar_per_group]
        index_2d.append(bar_positions)
        
    group_centers = []
    for group_idx in range(group_num):
        # 每组第一个bar的位置 + 每组最后一个bar的位置 → 除以2得中心
        group_first_bar = group_idx * (bar_per_group * (bar_width + intra_group_gap) + inter_group_gap)
        group_last_bar = group_first_bar + (bar_per_group - 1) * (bar_width + intra_group_gap)
        group_center = (group_first_bar + group_last_bar) / 2
        group_centers.append(group_center)

    for ax_index, ax in enumerate(axes):
        ax.set(xlabel='SFC Length', ylabel=list(watch_items.values())[ax_index])
        item = list(watch_items.keys())[ax_index]
        
        for i,algo in enumerate(algo_list):
            y_value = []
            for sfc_len in sfc_length_list:
                y_value.append(np.array(list(data[algo+'_'+str(sfc_len)][item].values()))[-1])

            ax.bar(index_2d[i],
                height=y_value,
                label=algo,
                color=color_Bar[i % len(color_Bar)],
                width=bar_width,
                edgecolor='black',
                linewidth=0.5)
            
            print(algo, item, ":" ,y_value)
        print()
        
        if ax_index == 0:
            def format_func(value, tick_number):
                return f'{value / 1e5:.1f}'
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))
            ax.set_ylabel(f'{list(watch_items.values())[ax_index]} (x$10^5$)')
        elif ax_index == 1:
            def format_func(value, tick_number):
                return f'{value / 1e6:.1f}'
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))
            ax.set_ylabel(f'{list(watch_items.values())[ax_index]} (x$10^6$)')

        ax.set_xticks(group_centers)  # 刻度位置
        ax.set_xticklabels(sfc_length_list)  # 刻度标签
        ax.tick_params(axis='x', rotation=0)

        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if ax_index == 1:
            ax.legend(frameon=False, loc='lower center', ncol=8, bbox_to_anchor=(0.5, 1))


    if not os.path.exists('fig'):
        os.makedirs('fig')

    fig.savefig('fig/fig_sfc_d_exp_'+title.replace(' ','_').lower()+'.svg',format='svg',dpi=150)
    fig.savefig('fig/fig_sfc_d_exp_'+title.replace(' ','_').lower()+'.pdf', bbox_inches='tight', pad_inches=0.5)


if __name__ == '__main__':
    main()

