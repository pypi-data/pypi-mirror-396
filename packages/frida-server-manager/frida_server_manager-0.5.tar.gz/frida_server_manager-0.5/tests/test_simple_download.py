#!/usr/bin/env python3
import sys
import os
import time
import subprocess

"""
简化的测试脚本：仅验证 frida-server 下载和解压缩功能，不涉及设备操作
"""

# 测试函数：直接测试 fsm.core 中的 download_frida_server 函数
def test_simple_download():
    print("开始测试 frida-server 下载和解压缩功能...")
    
    # 清理可能存在的临时文件
    print("清理临时文件...")
    try:
        # 删除可能存在的临时文件
        subprocess.run(["rm", "-f", "/tmp/frida-server-*"], check=False)
    except Exception as e:
        print(f"清理临时文件时出错: {e}")
    
    # 直接导入并调用 download_frida_server 函数
    try:
        # 添加项目路径到系统路径
        sys.path.append(".")
        
        # 导入 download_frida_server 函数
        from fsm.core import download_frida_server
        
        print("\n调用 download_frida_server 函数...")
        
        # 调用函数，使用特定版本避免获取最新版本的网络请求
        downloaded_file = download_frida_server(version="16.1.4", verbose=True)
        
        # 验证文件是否存在且大小合理
        if os.path.exists(downloaded_file) and os.path.getsize(downloaded_file) > 1000000:  # 文件大小应大于1MB
            print(f"\n✅ 测试成功: 文件成功下载并解压")
            print(f"下载的文件路径: {downloaded_file}")
            print(f"文件大小: {os.path.getsize(downloaded_file)} 字节")
            print("\n文件信息:")
            subprocess.run(["file", downloaded_file], check=False)
            return 0
        else:
            print("❌ 测试失败: 下载或解压的文件不存在或大小异常")
            return 1
    except Exception as e:
        print(f"❌ 测试失败: 发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    # 确保脚本可以被直接执行
    os.chmod(__file__, 0o755)
    
    # 运行测试并返回结果
    sys.exit(test_simple_download())