#!/usr/bin/env python3
import sys
import os
import time
import subprocess

"""
简化的测试脚本：直接验证fsm工具的ps和kill命令
"""

def run_command(cmd):
    """运行命令并显示输出"""
    print(f"\n执行命令: {cmd}")
    try:
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        print(f"返回码: {process.returncode}")
        if stdout:
            print(f"标准输出:\n{stdout}")
        if stderr:
            print(f"标准错误:\n{stderr}")
            
        return process.returncode
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return -1


def main():
    """主测试函数"""
    print("开始测试fsm工具的ps和kill命令...")
    
    # 测试ps命令
    print("\n测试ps命令:")
    return_code = run_command("python -m fsm ps")
    if return_code != 0:
        print("ps命令执行失败，检查错误输出")
        
    # 测试kill命令（不指定PID）
    print("\n测试kill命令（不指定PID）:")
    return_code = run_command("python -m fsm kill")
    if return_code != 0:
        print("kill命令执行失败，检查错误输出")
    
    # 再次测试ps命令，验证是否所有进程都已被杀死
    print("\n再次测试ps命令，验证是否所有进程都已被杀死:")
    return_code = run_command("python -m fsm ps")
    
    print("\n测试完成！")


if __name__ == "__main__":
    # 确保脚本可以被直接执行
    os.chmod(__file__, 0o755)
    main()