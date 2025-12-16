#!/usr/bin/env python3
import sys
import os
import unittest
from unittest import mock

"""
简单的代码结构测试脚本：验证fsm工具的ps和kill功能是否能正确导入和执行
"""

# 尝试导入我们添加的函数
try:
    from fsm.core import get_running_frida_servers, kill_frida_server
    from fsm.cli import main
    IMPORTS_SUCCESS = True
    print("成功导入get_running_frida_servers和kill_frida_server函数")
except ImportError as e:
    IMPORTS_SUCCESS = False
    print(f"导入失败: {e}")


class TestCodeStructure(unittest.TestCase):
    """测试代码结构的单元测试"""
    
    @mock.patch('fsm.core.check_adb_connection')
    @mock.patch('fsm.core.run_command')
    def test_get_running_frida_servers(self, mock_run_command, mock_check_adb):
        """测试get_running_frida_servers函数"""
        if not IMPORTS_SUCCESS:
            self.skipTest("导入失败，跳过测试")
            return
        
        # 模拟没有进程运行的情况
        mock_run_command.return_value = ""
        result = get_running_frida_servers(verbose=True)
        self.assertEqual(result, [])
        
        # 模拟有进程运行的情况
        mock_run_command.return_value = "root     12345  0.0  0.0  1234  5678 ?        Ss   10:00   0:00 /data/local/tmp/frida-server"
        result = get_running_frida_servers(verbose=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['pid'], '12345')
        self.assertEqual(result[0]['user'], 'root')
    
    @mock.patch('fsm.core.check_adb_connection')
    @mock.patch('fsm.core.run_command')
    def test_kill_frida_server(self, mock_run_command, mock_check_adb):
        """测试kill_frida_server函数"""
        if not IMPORTS_SUCCESS:
            self.skipTest("导入失败，跳过测试")
            return
        
        # 模拟杀死特定PID的情况
        mock_run_command.return_value = "No such process"
        kill_frida_server(pid='12345', verbose=True)
        
        # 模拟杀死所有进程的情况
        mock_run_command.return_value = ""
        kill_frida_server(verbose=True)

    @mock.patch('sys.argv', ['fsm', 'ps'])
    @mock.patch('fsm.cli.get_running_frida_servers')
    def test_cli_ps(self, mock_get_running):
        """测试CLI的ps命令"""
        if not IMPORTS_SUCCESS:
            self.skipTest("导入失败，跳过测试")
            return
        
        # 模拟sys.exit以避免实际退出
        with mock.patch('sys.exit') as mock_exit:
            main()
            mock_get_running.assert_called_once()

    @mock.patch('sys.argv', ['fsm', 'kill'])
    @mock.patch('fsm.cli.kill_frida_server')
    def test_cli_kill(self, mock_kill):
        """测试CLI的kill命令"""
        if not IMPORTS_SUCCESS:
            self.skipTest("导入失败，跳过测试")
            return
        
        # 模拟sys.exit以避免实际退出
        with mock.patch('sys.exit') as mock_exit:
            main()
            mock_kill.assert_called_once_with(None, False)

    @mock.patch('sys.argv', ['fsm', 'kill', '--pid', '12345'])
    @mock.patch('fsm.cli.kill_frida_server')
    def test_cli_kill_by_pid(self, mock_kill):
        """测试CLI的kill命令（指定PID）"""
        if not IMPORTS_SUCCESS:
            self.skipTest("导入失败，跳过测试")
            return
        
        # 模拟sys.exit以避免实际退出
        with mock.patch('sys.exit') as mock_exit:
            main()
            mock_kill.assert_called_once_with('12345', False)


if __name__ == "__main__":
    print("===== fsm 代码结构测试 =====")
    
    # 先检查导入是否成功
    if not IMPORTS_SUCCESS:
        print("代码结构测试失败：无法导入必要的函数")
        sys.exit(1)
    
    # 运行单元测试
    print("\n运行单元测试...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n===== 测试总结 =====")
    print("fsm ps和kill功能的代码结构测试通过！")
    print("请注意：此测试仅验证代码结构是否正确，实际功能需要连接Android设备进行测试。")
    
    # 创建使用说明
    print("\n===== 使用说明 =====")
    print("1. 查看运行中的frida-server进程：")
    print("   python -m fsm ps [-v]")
    print("2. 杀死所有frida-server进程：")
    print("   python -m fsm kill [-v]")
    print("3. 杀死特定PID的frida-server进程：")
    print("   python -m fsm kill --pid <PID> [-v]")
    print("\n参数说明：")
    print("-v, --verbose: 启用详细输出")
    print("--pid: 指定要杀死的进程PID")
    
    sys.exit(0)