
import os
import numpy as np
from astropy.time import Time
from dataclasses import dataclass

@dataclass(frozen=False)
class DATA_GROUP:
    """数据集"""
    
    TIME_SIM_START = Time("2021-07-22 00:00:00")
    """仿真开始时间"""
    
    
    # region ALL_ALGORITHMS
    DATA_ALL_ALGORITHMS = {
        'TagGatDrl':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251201072241923_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'PGRA':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251124182235707_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'DRLSFCP':  {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251125105409090_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'Pso':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251113223758849_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'LMSFCP':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251125165318191_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'TMSM':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251124110018431_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'Greedy':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251113205008738_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Random':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251113203023405_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
    }
    """相同场景下各种算法对比测试数据集"""

    # region ENV_RES_PERF
    DATA_ENV_RES_PERF = {
        # region TagGatDrl
        'TagGatDrl_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployGatDrl_0.5_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployGatDrl_1.0_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployGatDrl_1.5_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployGatDrl_2.0_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployGatDrl_2.5_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployGatDrl_2.5_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        # region TMSM
        'TMSM_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployTMSM_0.5_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployTMSM_1.0_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployTMSM_1.5_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployTMSM_2.0_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployTMSM_2.5_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployTMSM_2.5_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        # region Pso
        'Pso_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedPso_0.5_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedPso_1.0_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedPso_1.5_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedPso_2.0_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedPso_2.5_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedPso_2.5_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        # region PGRA
        'PGRA_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployPGRA_0.5_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployPGRA_1.0_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployPGRA_1.5_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployPGRA_2.0_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployPGRA_2.5_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployPGRA_2.5_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        # region DRLSFCP
        'DRLSFCP_0.5':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployDRLSFCP_0.5_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_1.0':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployDRLSFCP_1.0_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_1.5':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployDRLSFCP_1.5_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_2.0':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployDRLSFCP_2.0_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_2.5':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployDRLSFCP_2.5_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_3.0':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SolverDeployDRLSFCP_3.0_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        # region  LMSFCP
        'LMSFCP_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_0.5_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_1.0_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_1.5_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_2.0_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_2.5_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_2.5_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        
        # region Greedy
        'Greedy_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_0.5_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_1.0_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_1.5_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_2.0_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_2.5_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_2.5_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        # region Random
        'Random_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_0.5_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_1.0_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_1.5_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_2.0_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_2.5_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_env_resource\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_3.0_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
    }
    """不同基底网络资源量下不同算法对比测试数据集"""
    
    # region ENV_ARRIVAL_RATE
    DATA_ENV_ARRIVAL_RATE = {
        # region TagGatDrl
        'TagGatDrl_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployGatDrl_0.5_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployGatDrl_1.0_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployGatDrl_1.5_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployGatDrl_2.0_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployGatDrl_2.5_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployGatDrl_2.5_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        # region TMSM
        'TMSM_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployTMSM_0.5_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployTMSM_1.0_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployTMSM_1.5_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployTMSM_2.0_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployTMSM_2.5_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployTMSM_2.5_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        # region Pso
        'Pso_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedPso_0.5_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedPso_1.0_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedPso_1.5_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedPso_2.0_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedPso_2.5_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedPso_2.5_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        # region PGRA
        'PGRA_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployPGRA_0.5_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployPGRA_1.0_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployPGRA_1.5_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployPGRA_2.0_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployPGRA_2.5_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployPGRA_2.5_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        # region DRLSFCP
        'DRLSFCP_0.5':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployDRLSFCP_0.5_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_1.0':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployDRLSFCP_1.0_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_1.5':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployDRLSFCP_1.5_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_2.0':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployDRLSFCP_2.0_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_2.5':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployDRLSFCP_2.5_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_3.0':     {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployDRLSFCP_3.0_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        # region  LMSFCP
        'LMSFCP_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_0.5_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_1.0_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_1.5_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_2.0_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_2.5_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeployLMSFCP_2.5_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        
        # region Greedy
        'Greedy_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_0.5_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_1.0_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_1.5_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_2.0_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_2.5_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedGreedy_2.5_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        # region Random
        'Random_0.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_0.5_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_1.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_1.0_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_1.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_1.5_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_2.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_2.0_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_2.5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_2.5_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_3.0':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_arrive_rate\SfcdSagin_SfcdSagin_SolverDeploySharedRandom_3.0_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},

    }
    """不同SFC到达率下不同算法对比测试数据集"""

    # region ENV_SFC_SHARED
    DATA_ENV_SFC_SHARED = {
        # region TagGatDrl
        'TagGatDrl_Shared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployGatDrl_shared_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_Unshared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployGatDrl_unshared_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        # region TMSM
        'TMSM_Shared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployTMSM_shared_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_Unshared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployTMSM_unshared_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        # region Pso
        'Pso_Shared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeploySharedPso_shared_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_Unshared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeploySharedPso_unshared_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        # region PGRA
        'PGRA_Shared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployPGRA_shared_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_Unshared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployPGRA_unshared_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        # region DRLSFCP
        'DRLSFCP_Shared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployDRLSFCP_shared_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_Unshared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployDRLSFCP_unshared_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        # region LMSFCP
        'LMSFCP_Shared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployLMSFCP_shared_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_Unshared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeployLMSFCP_unshared_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        # region Greedy
        'Greedy_Shared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeploySharedGreedy_shared_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_Unshared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeploySharedGreedy_unshared_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        # region Random
        'Random_Shared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeploySharedRandom_shared_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_Unshared':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_shared\SfcdSagin_SolverDeploySharedRandom_unshared_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
    }
    """是否开启SFC共享情况下不同算法对比测试数据集"""

    # region ENV_SFC_LENGTH
    DATA_ENV_SFC_LENGTH = {
        # region TagGatDrl
        'TagGatDrl_3':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployGatDrl_3_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployGatDrl_5_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_7':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployGatDrl_7_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_9':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployGatDrl_9_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'TagGatDrl_11':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployGatDrl_11_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        # region TMSM
        'TMSM_3':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployTMSM_3_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployTMSM_5_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_7':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployTMSM_7_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_9':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployTMSM_9_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        'TMSM_11':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployTMSM_11_0\nfvo_deploy_SolverDeployTMSM.csv"),
            'data':{}},
        
        # region Pso
        'Pso_3':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedPso_3_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedPso_5_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_7':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedPso_7_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_9':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedPso_9_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'Pso_11':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedPso_11_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        # region PGRA
        'PGRA_3':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployPGRA_3_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployPGRA_5_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_7':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployPGRA_7_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_9':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployPGRA_9_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        'PGRA_11':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployPGRA_11_0\nfvo_deploy_SolverDeployPGRA.csv"),
            'data':{}},
        
        # region DRLSFCP
        'DRLSFCP_3':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployDRLSFCP_3_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployDRLSFCP_5_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_7':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployDRLSFCP_7_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_9':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployDRLSFCP_9_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        'DRLSFCP_11':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployDRLSFCP_11_0\nfvo_deploy_SolverDeployDRLSFCP.csv"),
            'data':{}},
        
        # region LMSFCP
        'LMSFCP_3':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployLMSFCP_3_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployLMSFCP_5_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_7':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployLMSFCP_7_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_9':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployLMSFCP_9_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        'LMSFCP_11':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeployLMSFCP_11_0\nfvo_deploy_SolverDeployLMSFCP.csv"),
            'data':{}},
        
        # region Greedy
        'Greedy_3':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedGreedy_3_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedGreedy_5_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_7':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedGreedy_7_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_9':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedGreedy_9_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        'Greedy_11':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedGreedy_11_0\nfvo_deploy_SolverDeploySharedGreedy.csv"),
            'data':{}},
        
        # region Random
        'Random_3':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedRandom_3_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_5':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedRandom_5_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_7':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedRandom_7_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_9':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedRandom_9_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
        
        'Random_11':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_sfc_length\SfcdSagin_SolverDeploySharedRandom_11_0\nfvo_deploy_SolverDeploySharedRandom.csv"),
            'data':{}},
    }
    """不同SFC长度下不同算法对比测试数据集"""

    # region TRAIN_TRACES_GEN_1
    DATA_TRAIN_TRACES_GEN_1 = {
        'Pso':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251113223758849_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'episode_1':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251202091808333_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
        'episode_2':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251202114933835_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
        'episode_3':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251202145814032_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
        'episode_4':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251202181235090_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
        'episode_5':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251202213008986_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
        'episode_6':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251203003623426_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
        'episode_7':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251203034349598_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
        'episode_8':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251203071310219_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
        'episode_9':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251203102222502_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
        'episode_10':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_1\SfcdSagin_Yilong15Pro_20251203134844543_0\nfvo_deploy_SolverDeployGatDrlV1.csv"),
            'data':{}},
        
    }
    """GatDrl训练过程数据集 (7特征不归一化)"""
    
    # region TRAIN_TRACES_GEN_2
    DATA_TRAIN_TRACES_GEN_2 = {
        'Pso':      {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251113223758849_0\nfvo_deploy_SolverDeploySharedPso.csv"),
            'data':{}},
        
        'episode_1':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251126212040051_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_2':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251127003622123_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_3':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251127023534004_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_4':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251127043744955_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_5':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251127065038703_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_6':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251127092306007_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_7':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251127130615339_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_8':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251127154549679_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_9':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251127174832566_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_10':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SolverDeployGatDrl_Train_Trace\gen_2\SfcdSagin_Yilong15Pro_20251127200301461_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
    }
    """GatDrl训练过程数据集 (9特征归一化)"""
    
    # region TRAIN_TRACES_GEN_3
    DATA_TRAIN_TRACES_GEN_3 = {
        # 'Pso':      {
        #     'filepath':
        #         os.path.normpath(
        #             r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251113223758849_0\nfvo_deploy_SolverDeploySharedPso.csv"),
        #     'data':{}},
        
        'episode_1':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251127225057500_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_2':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251128005328456_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_3':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251128030442827_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_4':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251128053434093_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_5':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251128080229159_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_6':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251128103815989_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_7':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251128135431195_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_8':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251128172019130_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_9':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251128213221367_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_10':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251129064300473_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_11':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251129104256952_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_12':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251129142901849_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_13':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251129173801941_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_14':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251129201809335_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_15':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251129225616249_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_16':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251130165601720_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_17':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251130203820754_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_18':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251201001431748_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_19':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251201035103905_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
        'episode_20':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d\SfcdSagin_Yilong15Pro_20251201072241923_0\nfvo_deploy_SolverDeployGatDrl.csv"),
            'data':{}},
        
    }
    """GatDrl训练过程数据集 (7特征归一化)"""
    
    # region TRAIN_TRACES_MELT_GAT
    DATA_TRAIN_TRACES_MELT_GAT = {
        'episode_1':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251202091731797_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_2':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251202121135639_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_3':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251202151254098_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_4':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251202184204667_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_5':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251202221945410_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_6':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251203013751322_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_7':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251203050702327_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_8':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251203083024604_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_9':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251203121258082_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_10':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251203154836974_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_11':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251203214944693_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_12':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251204021243729_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_13':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251204061114157_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_14':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251204095425921_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_15':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251204141622120_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_16':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251204230000134_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_17':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251205025448802_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_18':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251205062955654_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_19':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251205132607604_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
        
        'episode_20':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gat\SfcdSagin_Yilong15Pro_20251205212558670_0\nfvo_deploy_SolverDeployGatDrlMeltGat.csv"),
            'data':{}},
    }
    """相比GatDrl消融了GAT模块的训练结果"""
        
    # region TRAIN_TRACES_MELT_GRU
    DATA_TRAIN_TRACES_MELT_GRU = {
        'episode_1':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251202091735552_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_2':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251202120706129_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_3':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251202151037060_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_4':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251202183844853_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_5':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251202215115515_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_6':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251203010221142_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_7':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251203040826393_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_8':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251203072726684_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_9':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251203105632520_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_10':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251203141200991_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_11':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251203205201505_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_12':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251204005106695_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_13':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251204043741739_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_14':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251204081844293_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_15':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251204121720621_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_16':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251204162549293_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_17':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251204205107673_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_18':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251205013518828_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_19':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251205051726397_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
        'episode_20':   {
            'filepath':
                os.path.normpath(
                    r"E:\codelibrary\PYTHONWORK\NetOrchestr\examples\demo_sfc_d_melt_gru\SfcdSagin_Yilong15Pro_20251205092106785_0\nfvo_deploy_SolverDeployGatDrlMeltGru.csv"),
            'data':{}},
        
    }
    """相比GatDrl消融了GRU模块的训练结果"""
        

@dataclass(frozen=True)
class STYLE_DRAW:
    """绘图风格"""
    
    COLOUR_BAR_1 = np.array([
        [220, 20, 60],   # crimson (深红/绯红)
        [25, 25, 112],   # midnightblue (午夜蓝)
        [34, 139, 34],   # forestgreen (森林绿)
        [255, 165, 0],   # orange (橙色)
        [138, 43, 226],  # blueviolet (蓝紫色)
        [255, 99, 71],   # tomato (番茄红)
        [0, 255, 255],   # cyan (青色/蓝绿色)
        [128, 0, 128]    # purple (紫色)
    ]) / 255.0
    """颜色系列1: 包含8种颜色 深红、午夜蓝、森林绿、橙色、蓝紫色、番茄红、青色/蓝绿色、紫色"""
    
    COLOUR_BAR_2 = np.array([
        [209, 42, 32],    # firebrick (火砖红)
        [21, 29, 41],     # darkslategray (深青灰)
        [80, 138, 178],   # steelblue (钢青)
        [250, 192, 61],   # gold (金色)
        [213, 168, 130],  # peachpuff (桃色)
        [179, 106, 111],  # lightcoral (浅珊瑚红)
        [161, 208, 199],  # turquoise (绿松石色)
    ]) / 255.0
    """颜色系列2: 包含7种颜色 火砖红、深青灰、钢青、金色、桃色、浅珊瑚红、绿松石色"""
    
    COLOUR_BAR_3 = np.array([
        [209, 42, 32],    # firebrick (火砖红)，用于突出重要实验组
        [0, 0, 0],        # black (纯黑)，用于基准组或对照数据
        [230, 159, 0],    # orange (橙黄)，高辨识度，无混淆风险
        [86, 180, 233],   # skyblue (天蓝)，色调清爽，视觉舒适
        [0, 158, 115],    # teal (青绿色)，区别于常规绿色，辨识度高
        [240, 233, 67],   # khaki (卡其黄)，柔和不刺眼
        [0, 114, 178],    # royalblue (宝蓝)，沉稳的深色系
        [171, 104, 183],  # mediumpurple (中紫色)，填补紫色系空缺
        [102, 102, 102]   # slategrey (石板灰)，适配多组对比的补充色
    ]) / 255.0
    """颜色系列3: Okabe - Ito 拓展 (色盲友好, 顶刊首选，适配各类对比图，黑白打印可区分), 包含9种颜色 纯黑、橙黄、天蓝、青绿色、卡其黄、宝蓝、朱红、中紫色、石板灰"""
    
    COLOUR_BAR_4 = np.array([
        [209, 42, 32],    # firebrick (火砖红)，用于突出重要实验组
        [66, 113, 178],   # natureblue (自然蓝)，顶刊常用主色
        [217, 83, 25],    # burntorange (焦橙)，对比鲜明不刺眼
        [119, 172, 48],   # limegreen (酸橙绿)，区别于常规绿色
        [126, 47, 142],   # plum (李子紫)，低饱和不突兀
        [76, 183, 172],   # tealblue (青蓝)，填补冷色空缺
        [237, 177, 32],   # amber (琥珀黄)，柔和的暖色
        [179, 106, 111],  # roseash (玫瑰灰)，独特且不抢眼
        [95, 95, 95]      # darkgrey (深灰)，适配补充对照组
    ]) / 255.0
    """颜色系列4: Nature 质感款 (色调协调, 视觉雅致, 符合顶刊审美, 适配多场景科研作图), 包含9种颜色 自然蓝、焦橙、酸橙绿、酒红、李子紫、青蓝、琥珀黄、玫瑰灰、深灰"""
    
    LINESTYLE_BAR = ['-', '--', '-.', ':', (0, (1, 10)), (0, (5, 5)), (0, (3, 5, 1, 5))]
    """线型系列"""
    
    MARKER_BAR = ['o', 's', '^', 'v', '<', '>', 'p', '*', 'h', 'D']
    """标记系列"""

    HATCH_BAR = ['','/','+','\\','|','-','x']
    """填充图案系列"""
