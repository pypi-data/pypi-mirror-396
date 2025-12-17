#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-

'''
scave_solver_train_melt.py
==========================

.. module:: scave_solver_train_melt
  :platform: Windows
  :synopsis: 该模块用于解析 NetOrchestra 仿真器输出的 MANO 求解器输出的训练过程的日志数据, 并绘制消融实验中训练过程随时间变化的图表.

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
from netorchestr.common.util import DataAnalysis
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

    data_gat_drl = DATA_GROUP.DATA_TRAIN_TRACES_MELT_GAT
    data_melt_gat = DATA_GROUP.DATA_TRAIN_TRACES_GEN_3
    data_melt_gru = DATA_GROUP.DATA_TRAIN_TRACES_MELT_GRU

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

    def __get_migration_rate_from_file(filepath:str):
        data = pd.read_csv(filepath)
        dataFrame = np.array(copy.deepcopy(data[['Event','Result']]))
        set_success_num = 0
        migration_times = 0
        for i in range(len(dataFrame)):
            if dataFrame[i][0] == '+' and dataFrame[i][1] == True:
                set_success_num += 1
            if dataFrame[i][0] == 'd':
                migration_times += 1
        return migration_times/set_success_num


    # region 开始绘图

    title ='Solver Training Process Comparison Melting'

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

    for episode_index in data_gat_drl.keys():
        for item in list(watch_items.keys()):
            data_gat_drl[episode_index][item] = __get_array_from_file(data_gat_drl[episode_index]['filepath'], watch_item=item)
    for episode_index in data_melt_gat.keys():
        for item in list(watch_items.keys()):
            data_melt_gat[episode_index][item] = __get_array_from_file(data_melt_gat[episode_index]['filepath'], watch_item=item)
    for episode_index in data_melt_gru.keys():
        for item in list(watch_items.keys()):
            data_melt_gru[episode_index][item] = __get_array_from_file(data_melt_gru[episode_index]['filepath'], watch_item=item)

    for ax_index, ax in enumerate(axes):
        ax.set(xlabel='Episode', ylabel=list(watch_items.values())[ax_index])
        item = list(watch_items.keys())[ax_index]
        
        x_value = np.arange(1, len(data_gat_drl.keys())+1) * 300
        y_value = []
        for i,episode_index in enumerate(data_gat_drl.keys()):
            y_value.append(np.array(list(data_gat_drl[episode_index][item].values()))[-1])
        ax.plot(x_value,y_value,color=color_Bar[0],linestyle=linestyle_Bar[0],marker=marker_Bar[0],markersize=4,label='TAG-GAT-DRL')
        
        x_value = np.arange(1, len(data_melt_gat.keys())+1) * 300
        y_value = []
        for i,episode_index in enumerate(data_melt_gat.keys()):
            y_value.append(np.array(list(data_melt_gat[episode_index][item].values()))[-1])
        ax.plot(x_value,y_value,color=color_Bar[1],linestyle=linestyle_Bar[1],marker=marker_Bar[1],markersize=4,label='MELT-GAT')
        
        x_value = np.arange(1, len(data_melt_gru.keys())+1) * 300
        y_value = []
        for i,episode_index in enumerate(data_melt_gru.keys()):
            y_value.append(np.array(list(data_melt_gru[episode_index][item].values()))[-1])
        ax.plot(x_value,y_value,color=color_Bar[3],linestyle=linestyle_Bar[2],marker=marker_Bar[2],markersize=4,label='MELT-GRU')

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
        
        if ax_index == 1:
            ax.legend(loc='lower center',bbox_to_anchor=(0.5, 1),frameon=False,ncol=3)


    # watch_items = {
    #     "sfcSetRate":"SFC Set Success Rate",
    #     "sfcCompleteRate":"SFC Complete Rate",
    #     "sfcMigrationRate":"SFC Migration Rate",
    # }
    # for ax_index, ax in enumerate(axes[1]):
    #     ax.set(xlabel='Episode', ylabel=list(watch_items.values())[ax_index])
    #     item = list(watch_items.keys())[ax_index]
        
    #     if ax_index == 0 or ax_index == 1:
    #         x_value = np.arange(1, len(data_gat_drl.keys())+1) * 300
    #         y_value = []
    #         for i,episode_index in enumerate(data_gat_drl.keys()):
    #             y_value.append(DataAnalysis.getResult(data_gat_drl[episode_index]['filepath'], print_flag=False, draw_flag=False)[item])
    #         ax.plot(x_value,y_value,color=color_Bar[0],linestyle=linestyle_Bar[0],marker=marker_Bar[0],markersize=4,label='GAT-DRL')
            
    #         x_value = np.arange(1, len(data_melt_gat.keys())+1) * 300
    #         y_value = []
    #         for i,episode_index in enumerate(data_melt_gat.keys()):
    #             y_value.append(DataAnalysis.getResult(data_melt_gat[episode_index]['filepath'], print_flag=False, draw_flag=False)[item])
    #         ax.plot(x_value,y_value,color=color_Bar[1],linestyle=linestyle_Bar[1],marker=marker_Bar[1],markersize=4,label='MELT-GAT')
            
    #         x_value = np.arange(1, len(data_melt_gru.keys())+1) * 300
    #         y_value = []
    #         for i,episode_index in enumerate(data_melt_gru.keys()):
    #             y_value.append(DataAnalysis.getResult(data_melt_gru[episode_index]['filepath'], print_flag=False, draw_flag=False)[item])
    #         ax.plot(x_value,y_value,color=color_Bar[3],linestyle=linestyle_Bar[2],marker=marker_Bar[2],markersize=4,label='MELT-GRU')

    #     elif ax_index == 2:
    #         x_value = np.arange(1, len(data_gat_drl.keys())+1) * 300
    #         y_value = []
    #         for i,episode_index in enumerate(data_gat_drl.keys()):
    #             y_value.append(__get_migration_rate_from_file(data_gat_drl[episode_index]['filepath']))
    #         ax.plot(x_value,y_value,color=color_Bar[0],linestyle=linestyle_Bar[0],marker=marker_Bar[0],markersize=4,label='GAT-DRL')
            
    #         x_value = np.arange(1, len(data_melt_gat.keys())+1) * 300
    #         y_value = []
    #         for i,episode_index in enumerate(data_melt_gat.keys()):
    #             y_value.append(__get_migration_rate_from_file(data_melt_gat[episode_index]['filepath']))
    #         ax.plot(x_value,y_value,color=color_Bar[1],linestyle=linestyle_Bar[1],marker=marker_Bar[1],markersize=4,label='MELT-GAT')
            
    #         x_value = np.arange(1, len(data_melt_gru.keys())+1) * 300
    #         y_value = []
    #         for i,episode_index in enumerate(data_melt_gru.keys()):
    #             y_value.append(__get_migration_rate_from_file(data_melt_gru[episode_index]['filepath']))
    #         ax.plot(x_value,y_value,color=color_Bar[3],linestyle=linestyle_Bar[2],marker=marker_Bar[2],markersize=4,label='MELT-GRU')

    #     ax.legend(loc='lower center',bbox_to_anchor=(0.5, 1),frameon=False,ncol=3)
    #     ax.grid(True, linestyle='--', alpha=0.6)
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
        
    if not os.path.exists('fig'):
        os.makedirs('fig')

    fig.savefig('fig/fig_sfc_d_exp_'+title.replace(' ','_').lower()+'.svg',format='svg',dpi=150)
    fig.savefig('fig/fig_sfc_d_exp_'+title.replace(' ','_').lower()+'.pdf', bbox_inches='tight', pad_inches=0.5)


if __name__ == '__main__':
    main()

