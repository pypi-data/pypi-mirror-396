#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   dataAnalysis.py
@Time    :   2024/06/20 21:03:17
@Author  :   Wang Xi
@Version :   0.0
@Contact :   wangxi_chn@foxmail.com
@License :   (C)Copyright 2023-2024, Wang Xi
@Desc    :   None
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import code
import os

class DataExtractor:
    def __init__(self,filename:str) -> None:
        self.filename = filename
    
    def extract(self,header:list[str]):
        data = pd.read_csv(self.filename)
        return(data[header])

class DataAnalysis:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def getResult(filename:str, print_flag:bool=True, draw_flag:bool=True):
        dataExtractor = DataExtractor(filename)
        dataFrame = dataExtractor.extract(['Event','Result'])
        dataFrame_array = np.array(dataFrame)
        dataFrame_list = dataFrame_array.tolist()

        sfcNum = 0
        sfcSetNum = 0
        sfcCompleteNum = 0

        for i in range(len(dataFrame_list)):
            if dataFrame_list[i][0] == '+':
                sfcNum += 1
                if dataFrame_list[i][1] == True:
                    sfcSetNum += 1
            elif dataFrame_list[i][0] == '-':
                if dataFrame_list[i][1] == True:
                    sfcCompleteNum += 1
        
        assert sfcNum != 0, ValueError(f'No "+" event in {filename}')
        
        resultReportDict = {'sfcNum':sfcNum,
                            'sfcSetNum':sfcSetNum,
                            'sfcSetRate':sfcSetNum/sfcNum,
                            'sfcCompleteNum':sfcCompleteNum,
                            'sfcCompleteRate':sfcCompleteNum/sfcNum
                            }

        if print_flag:
            print(f'INFO: Analysis Trace {filename}|')
            for key, value in resultReportDict.items():
                print(f'\t{key}: {value}')
        
        if draw_flag:
            dataFrame = dataExtractor.extract(['Reason'])
            condition_counts = dataFrame.value_counts()
            condition_counts_sorted = condition_counts.sort_index()
            print("\nINFO: Analysis Trace Condition counts:")
            for idx, count in condition_counts_sorted.items():
                # 处理多索引情况（如果Reason是单一列，idx会是元组形式）
                reason = idx[0] if isinstance(idx, tuple) else idx
                print(f'\t{reason}: {count}')
            
            # 绘制成分占比前需移除指定条目（SET_SUCCESS属于重复计数项目要移除）
            target = 'SOLUTION_DEPLOY_TYPE.SET_SUCCESS'
            if target in condition_counts.index.get_level_values(0):
                condition_counts = condition_counts.drop(target, level=0)
                
            plt.figure(figsize=(10, 8))  # 增大画布尺寸，给文字更多空间
            wedges, texts, autotexts = plt.pie(
                condition_counts,
                labels=condition_counts.index,
                autopct='%1.1f%%',
                startangle=90,
                pctdistance=0.85,  # 百分比标签距离圆心的距离
                labeldistance=1.1,  # 元素标签距离圆心的距离（调大避免重叠）
                wedgeprops=dict(width=0.6),  # 可选：将饼图改为"环形图"，减少中心拥挤
                rotatelabels=True  # 旋转标签，避免水平重叠
            )
            plt.setp(texts, size=10, wrap=True)  # 减小字体，自动换行
            plt.setp(autotexts, size=8, color='white', weight='bold')
            plt.axis('equal')
            plt.savefig(
                os.path.join(os.path.dirname(filename), f'{filename}_reason.png'),
                dpi=300,
                bbox_inches='tight'  # 保存时包含所有元素，避免文字被裁剪
            )
            plt.close()

        return resultReportDict
    
    
    @staticmethod
    def format_milliseconds(ms, languange='cn'):
        """
        格式化毫秒为时分秒毫秒

        Args:
            ms (int): 毫秒
            languange (str, optional): 语言类型, cn/en. Defaults to 'cn'.

        Returns:
            str: 格式化后的字符串
        """
        # 确保输入是整数
        ms = int(ms)

        hours = ms // 3600000  # 1小时 = 3600000毫秒
        ms %= 3600000
        minutes = ms // 60000   # 1分钟 = 60000毫秒
        ms %= 60000
        seconds = ms // 1000    # 1秒 = 1000毫秒
        ms %= 1000
        
        # 格式化输出
        if languange == 'cn':
            return f"{hours}小时:{minutes}分钟:{seconds}秒:{ms}毫秒"
        elif languange == 'en':
            return f"{hours}h:{minutes}m:{seconds}s:{ms}ms"
            

        
        


    



