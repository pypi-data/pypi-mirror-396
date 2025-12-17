
# 按照参考文献中各个算法介绍的发表时间顺序（倒叙），依次实现了以下求解器：

from .solver_deploy_base import SolverDeployBase, SolverDeploySharedBase, SolutionDeploy, SOLUTION_DEPLOY_TYPE
from .solver_deploy_random import SolverDeploySharedRandom              # 逻辑测试 √ 性能验证 √
from .solver_deploy_greedy import SolverDeploySharedGreedy              # 逻辑测试 √ 性能验证 √
from .solver_deploy_pso import SolverDeploySharedPso                    # 逻辑测试 √ 性能验证 √
from .solver_deploy_gatdrl import SolverDeployGatDrl                    # 逻辑测试 √ 性能验证 √
from .solver_deploy_gatdrl_v1 import SolverDeployGatDrlV1               # 逻辑测试 √ 性能验证 √
from .solver_deploy_gatdrl_melt_gat import SolverDeployGatDrlMeltGat    # 逻辑测试 √ 性能验证 √
from .solver_deploy_gatdrl_melt_gru import SolverDeployGatDrlMeltGru    # 逻辑测试 √ 性能验证 √
from .solver_deploy_pgarl import SolverDeployPGARL                      # 逻辑测试 √ 性能验证 √
from .solver_deploy_pposfc import SolverDeployPPOSFC                    # 逻辑测试 √ 性能验证 ×
from .solver_deploy_lm_sfcp import SolverDeployLMSFCP                   # 逻辑测试 √ 性能验证 √
from .solver_deploy_tmsm import SolverDeployTMSM                        # 逻辑测试 √ 性能验证 √
from .solver_deploy_dvine import SolverDeployDVine                      # 逻辑测试 × 性能验证 ×
from .solver_deploy_gep import SolverDeployGEP                          # 逻辑测试 × 性能验证 ×
from .solver_deploy_ts_mapsch import SolverDeployTSMAPSCH               # 逻辑测试 × 性能验证 ×
from .solver_deploy_ts_psch import SolverDeployTSPSCH                   # 逻辑测试 × 性能验证 ×
from .solver_deploy_pgra import SolverDeployPGRA                        # 逻辑测试 √ 性能验证 √
from .solver_deploy_drlsfcp import SolverDeployDRLSFCP                  # 逻辑测试 √ 性能验证 √
from .solver_deploy_vna import SolverDeployVNA                          # 逻辑测试 × 性能验证 ×

import importlib
import inspect

def get_all_solver_classes():
    """自动获取所有求解器类"""
    module_name = "netorchestr.envir.node.controller.mano.solver_deploy"
    module = importlib.import_module(module_name)
    
    # 获取模块中所有的类
    solver_classes = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if name.startswith("SolverDeploy"):
            solver_classes.append(name)
    
    return solver_classes

def import_solver(solver_name):
    all_solver_classes = get_all_solver_classes()
    if solver_name not in all_solver_classes:
        raise ValueError(f"无法导入模块 {solver_name}, 暂时支持的有效求解器为：{all_solver_classes}")
    
    module = importlib.import_module("netorchestr.envir.node.controller.mano.solver_deploy")
    return getattr(module, solver_name)


def solver_help():
    """打印所有求解器的帮助信息"""
    all_solver_classes = get_all_solver_classes()
    formatted_solvers = ", ".join(all_solver_classes)
    
    solver_help_info = (
        f'服务功能链编排求解器类型, 默认为SolverDeploySharedRandom, '
        f'可选值：{formatted_solvers}'
    )
    return solver_help_info
    
SOLVER_HELP_INFO = solver_help()
    