
import os
import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():

    # region 定义风格
    from netorchestr.scave import STYLE_DRAW
    color_Bar = STYLE_DRAW.COLOUR_BAR_4
    linestyle_Bar = STYLE_DRAW.LINESTYLE_BAR
    marker_Bar = STYLE_DRAW.MARKER_BAR
    hatch_Bar = STYLE_DRAW.HATCH_BAR
    # endregion

    # region 获取数据
    from netorchestr.scave import DATA_GROUP
    init_time = DATA_GROUP.TIME_SIM_START
    data = DATA_GROUP.DATA_ALL_ALGORITHMS

    condition_types = ['Complete', 'Deploy fail for latency', 'Deploy fail for resource', 'Change fail for latency', 'Change fail for resource']

    def __get_array_from_file(filename:str):
        data = pd.read_csv(filename)
        dataFrame = np.array(copy.deepcopy(data[['Event','SfcId','Result','Reason']]))
        
        CounterDict = {condition_name:0 for condition_name in condition_types}

        CounterFilter = {
            condition_types[0]: [],
            condition_types[1]: ['SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_LATENCY',
                                'SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_START',
                                'SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_END',
                                'SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH',],
            condition_types[2]: ['SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_CPU',
                                'SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_RAM',
                                'SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_ROM'
                                'SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_LINK_BAND'],
            condition_types[3]: ['SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_LATENCY',
                                'SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_UE_ACCESS_START',
                                'SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_UE_ACCESS_END',
                                'SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH',],
            condition_types[4]: ['SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_CPU',
                                'SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_RAM',
                                'SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_ROM'
                                'SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_LINK_BAND'],
        }
        
        for i in range(len(dataFrame)):
            if dataFrame[i][0] == '+' and dataFrame[i][3] in CounterFilter['Deploy fail for latency']:      # 1
                CounterDict['Deploy fail for latency'] += 1
            elif dataFrame[i][0] == '+' and dataFrame[i][3] in CounterFilter['Deploy fail for resource']:   # 2
                CounterDict['Deploy fail for resource'] += 1
            elif dataFrame[i][0] == 'd' and dataFrame[i][3] in CounterFilter['Change fail for latency']:    # 3
                CounterDict['Change fail for latency'] += 1
            elif dataFrame[i][0] == 'd' and dataFrame[i][3] in CounterFilter['Change fail for resource']:   # 4
                CounterDict['Change fail for resource'] += 1
            elif dataFrame[i][0] == '-' and dataFrame[i][2] == True:
                CounterDict['Complete'] += 1

        sfc_num = np.max(data['SfcId'])+1

        return np.array(list(CounterDict.values()))/sfc_num

    for algo in data.keys():
        data[algo]['data'] = __get_array_from_file(f"{data[algo]['filepath']}")

    dataReshape = []
    for key in list(data.keys()):
        dataReshape.append(data[key]['data'])
    dataReshape = np.array(dataReshape).T

    # region 开始绘图

    labelslist = condition_types

    title ='Ochestrate Condition Over Different Algorithms'
    xlabel='Different algorithms'
    ylabel='Condition ratio'

    fig = plt.figure(figsize=(8, 3))
    ax = plt.axes()
    ax.set(xlabel=xlabel,ylabel=ylabel)

    bar_width = 0.1                                 # bar宽度（可调整）
    bar_per_group = 1                               # 每组bar数量（1个/组，需2个/组时改为2）
    group_num = int(len(data.keys())/bar_per_group) # 总分组数（根据需求设置）
    intra_group_gap = 0.05                          # 组内间距（小于组间间距）
    inter_group_gap = 0.1                           # 组间间距（大于组内间距）

    index_array = []
    for group_idx in range(group_num):
        # 计算当前组的基准位置
        group_base = group_idx * (bar_per_group * bar_width + inter_group_gap)
        # 计算组内每个bar的索引
        for bar_idx in range(bar_per_group):
            bar_pos = group_base + bar_idx * (bar_width + intra_group_gap)
            index_array.append(bar_pos)

    # 绘制堆叠柱状图
    for i, label in enumerate(condition_types):
        bottom = np.sum(dataReshape[0:i,:], axis=0) if i > 0 else np.zeros(len(data.keys()))
        ax.bar(index_array,
            height=dataReshape[i,:],
            bottom=bottom,
            label=label,
            color=color_Bar[i % len(color_Bar)],
            hatch=hatch_Bar[i % len(hatch_Bar)]*2,
            width=bar_width,
            edgecolor='black',  # 增加边框，区分不同条件
            linewidth=0.5)

    ax.grid(True, linestyle='--', alpha=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(frameon=False, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 1))

    plt.xticks(index_array,list(data.keys()),rotation=0)
    plt.tight_layout()

    if not os.path.exists('fig'):
        os.makedirs('fig')
    fig.savefig('fig/'+title.replace(' ','_')+'.svg',format='svg',dpi=150)
    fig.savefig('fig/'+title.replace(' ','_')+'.pdf', bbox_inches='tight', pad_inches=0.5)


if __name__ == '__main__':
    main()

