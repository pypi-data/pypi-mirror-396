#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-

'''
scave_solver_train_growth.py
==============================

.. module:: scave_solver_train_growth
  :platform: Windows
  :synopsis: 该模块用于解析 NetOrchestra 仿真器输出的 MANO 求解器输出的训练过程的日志数据, 并绘制训练过程随时间变化的图表.

.. moduleauthor:: WangXi

简介
----

该模块实现了从 NetOrchestra 仿真器输出的 MANO 数据中解析求解器训练过程数据, 主要用于网络编排和虚拟网络功能 VNF 部署的研究与分析中. 
它提供了以下特性:

- 解析 CSV 文件以获取训练过程数据.
- 使用 matplotlib 库绘制训练过程随时间变化的图表.
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


def main():

    # region 定义风格
    from netorchestr.scave import STYLE_DRAW
    color_Bar = STYLE_DRAW.COLOUR_BAR_4
    linestyle_Bar = STYLE_DRAW.LINESTYLE_BAR
    marker_Bar = STYLE_DRAW.MARKER_BAR

    # region 获取数据
    from netorchestr.scave import DATA_GROUP
    init_time = DATA_GROUP.TIME_SIM_START
    data = DATA_GROUP.DATA_TRAIN_TRACES_GEN_1

    def __get_array_from_file(filepath:str, watch_item:str='SysRevCostRatio'):
        data = pd.read_csv(filepath)
        dataFrame = np.array(copy.deepcopy(data[['Time',watch_item]]))
        dataFrame_dict = {}
        for i in range(len(dataFrame)):
            if i == 0:
                dataFrame_dict[init_time + (4.0 * u.hour)] = 0
                continue
            
            time_ms = dataFrame[i][0] * u.ms
            time_real = init_time + time_ms
            
            # 计算系统长期平均收益支出比
            sys_longtime_avg_revenue = float(dataFrame[i][1])/(time_ms.to(u.min).value)
            # 计算系统收益支出比
            sys_revenue = float(dataFrame[i][1])
            
            dataFrame_dict[time_real] = sys_revenue
        
        return dataFrame_dict

    watch_items = ['SysRevCostRatio', 'SysRev', 'SysCost']
    for algo in data.keys():
        for item in watch_items:
            data[algo][item] = __get_array_from_file(data[algo]['filepath'], watch_item=item)

    # region 开始绘图

    title ='Solver Training Process'

    wspace=0.5
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=((5+wspace)*3, 10), sharex=False)
    # fig.suptitle(title, y=1.2)
    fig.subplots_adjust(wspace=wspace)

    for ax_index, ax in enumerate(axes[0]):
        xlabel='Time'
        ax.set(xlabel=xlabel, ylabel=watch_items[ax_index])
        item = watch_items[ax_index]
        
        for i,algo in enumerate(data.keys()):
            time_astropy:list[Time] = list(data[algo][item].keys())
            time_datetime = [t.to_datetime() for t in time_astropy]
            sys_revenue = list(data[algo][item].values())
            
            ax.plot(time_datetime,
                    sys_revenue,
                    label=str(algo),
                    color=color_Bar[i %len(color_Bar)],
                    linestyle=linestyle_Bar[i %len(linestyle_Bar)],
                    marker=marker_Bar[i %len(marker_Bar)],
                    markersize=4,
                    markevery=50)

        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.legend(frameon=False, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 1))

    for ax_index, ax in enumerate(axes[1]):
        xlabel='Episode'
        ax.set(xlabel=xlabel, ylabel=watch_items[ax_index])
        item = watch_items[ax_index]
        
        x_value = np.arange(1, len(data.keys())+1)
        y_value = []
        for i,algo in enumerate(data.keys()):
            y_value.append(np.array(list(data[algo][item].values()))[-1])

        ax.plot(x_value,
                y_value,
                color=color_Bar[0],
                linestyle=linestyle_Bar[0],
                marker=marker_Bar[0],
                markersize=4)

        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    if not os.path.exists('fig'):
        os.makedirs('fig')

    fig.savefig('fig/'+title.replace(' ','_')+'.svg',format='svg',dpi=150)
    fig.savefig('fig/'+title.replace(' ','_')+'.pdf', bbox_inches='tight', pad_inches=0.5)


if __name__ == '__main__':
    main()

