#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-

'''
scave_net_sys_perf_solver_realtime.py
=====================================

.. module:: scave_net_sys_perf_solver_realtime
  :platform: Windows
  :synopsis: 该模块用于解析 NetOrchestra 仿真器输出的 MANO 部署过程的日志数据, 并绘制不同求解器算法下网络系统性能随时间变化的图表.

.. moduleauthor:: WangXi

简介
----

该模块实现了从 NetOrchestra 仿真器输出的 MANO 数据中解析网络系统性能的功能, 主要用于网络编排和虚拟网络功能 VNF 部署的研究与分析中. 
它提供了以下特性:

- 解析 CSV 文件以获取系统性能数据.
- 使用 matplotlib 库绘制不同求解器算法下网络系统性能随时间变化的图表.
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
from astropy.time import Time
import matplotlib.dates as mdates
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
    data = DATA_GROUP.DATA_ALL_ALGORITHMS

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
            
            watch_value = float(dataFrame[i][1])
            
            dataFrame_dict[time_real] = watch_value
        
        return dataFrame_dict

    # region 开始绘图

    title ='Network System Performance Over Different Algorithms'

    wfig=5
    hfig=3
    wspace=0.2
    hspace=0.3
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=((wfig+wspace)*3, (hfig+hspace)*1), sharex=False)
    # fig.suptitle(title, y=1.2)
    fig.subplots_adjust(wspace=wspace,hspace=hspace)

    watch_items = {
        "SysRev":"System Revenue",
        "SysCost":"System Cost",
        "SysRevCostRatio":"System Revenue Cost Ratio",
    }

    for algo in data.keys():
        for item in list(watch_items.keys()):
            data[algo][item] = __get_array_from_file(data[algo]['filepath'], watch_item=item)

    for ax_index, ax in enumerate(axes):
        ax.set(xlabel='Time', ylabel=list(watch_items.values())[ax_index])
        item = list(watch_items.keys())[ax_index]
        
        for i,algo in enumerate(data.keys()):
            time_astropy:list[Time] = list(data[algo][item].keys())
            time_datetime = [t.to_datetime() for t in time_astropy]
            sys_perf = list(data[algo][item].values())
            
            ax.plot(time_datetime,
                    sys_perf,
                    label=str(algo),
                    color=color_Bar[i %len(color_Bar)],
                    linestyle=linestyle_Bar[i %len(linestyle_Bar)],
                    marker=marker_Bar[i %len(marker_Bar)],
                    markersize=4,
                    markevery=50)
            
            print(f'{algo} |    {item} |    {sys_perf[-1]}')
        
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

        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        if ax_index == 1:
            ax.legend(loc='lower center',bbox_to_anchor=(0.5, 1),frameon=False,ncol=8)
        
        
    if not os.path.exists('fig'):
        os.makedirs('fig')

    fig.savefig('fig/fig_sfc_d_exp_'+title.replace(' ','_').lower()+'.svg',format='svg',dpi=150)
    fig.savefig('fig/fig_sfc_d_exp_'+title.replace(' ','_').lower()+'.pdf', bbox_inches='tight', pad_inches=0.5)


if __name__ == '__main__':
    main()

