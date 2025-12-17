import time
import subprocess

def run_target_script(file, params):
    """调用外部Python文件的函数, 实时输出内容"""
    time_start = time.time()
    
    cmd = ["python", file] + params
    print(f"执行命令：{' '.join(cmd)}")
    try:
        subprocess.run(cmd)
        
    except Exception as e:
        return f"执行失败: 发生错误 - {str(e)}"
    
    time_end = time.time()
    time_uesed = time_end - time_start
    
    return f"执行完成, 耗时：{time_uesed:.2f}秒"

def main():
    scave_script_cmd = {
        "scave_solver_train_melt.py": [],
        "scave_net_sys_perf_solver_realtime.py": [],
        
        "scave_net_sys_perf_sfc_shared.py": [],
        "scave_net_sys_perf_sfc_length.py": [],
        
        "scave_net_sys_perf_env_resource.py": [],
        "scave_net_sys_perf_sfc_arrival_rate.py": [],
    }
    
    for key, value in scave_script_cmd.items():
        print("#"*20 + f"正在执行脚本：{key}" + "#"*20)
        result = run_target_script(key, value)
        print(result)
        print()

if __name__ == "__main__":
    main()
