#!/usr/bin/env python3
import sys
import os
import time
import subprocess

"""
测试脚本：验证fsm工具的ps和kill功能
"""

def run_command(cmd, verbose=True):
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
        
        if verbose:
            print(f"返回码: {process.returncode}")
            if stdout:
                print(f"标准输出:\n{stdout}")
            if stderr:
                print(f"标准错误:\n{stderr}")
        
        return process.returncode, stdout, stderr
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return -1, "", str(e)


def test_ps_kill():
    """测试ps和kill功能"""
    print("开始测试fsm工具的ps和kill功能...")
    
    # 检查ADB连接
    print("\n检查ADB连接...")
    return_code, _, _ = run_command("adb devices")
    if return_code != 0:
        print("ADB未连接或未在PATH中，测试无法继续")
        return False
    
    # 测试ps命令
    print("\n测试ps命令（查看运行中的frida-server进程）:")
    return_code, stdout, stderr = run_command("python -m fsm ps")
    if return_code != 0:
        print("ps命令执行失败")
        return False
    
    # 如果没有运行中的frida-server进程，尝试启动一个
    if "No running frida-server processes found" in stdout:
        print("\n没有运行中的frida-server进程，尝试启动一个...")
        return_code, _, _ = run_command("python -m fsm run")
        if return_code != 0:
            print("启动frida-server失败，可能需要先安装")
            print("尝试安装frida-server...")
            return_code, _, _ = run_command("python -m fsm install")
            if return_code != 0:
                print("安装frida-server失败，测试无法继续")
                return False
            
            # 安装后再次尝试启动
            return_code, _, _ = run_command("python -m fsm run")
            if return_code != 0:
                print("启动frida-server失败，测试无法继续")
                return False
        
        # 等待frida-server启动
        time.sleep(2)
        
        # 再次测试ps命令
        print("\n再次测试ps命令（查看新启动的frida-server进程）:")
        return_code, stdout, stderr = run_command("python -m fsm ps")
        if return_code != 0:
            print("ps命令执行失败")
            return False
    
    # 测试kill命令
    print("\n测试kill命令（杀死所有frida-server进程）:")
    return_code, _, _ = run_command("python -m fsm kill")
    if return_code != 0:
        print("kill命令执行失败")
        return False
    
    # 验证所有进程都已被杀死
    print("\n验证所有frida-server进程都已被杀死:")
    return_code, stdout, stderr = run_command("python -m fsm ps")
    if "No running frida-server processes found" in stdout:
        print("验证成功：所有frida-server进程都已被杀死")
    else:
        print("验证失败：仍然有frida-server进程在运行")
        return False
    
    return True


def test_kill_by_pid():
    """测试按PID杀死特定进程的功能"""
    print("\n测试按PID杀死特定进程的功能...")
    
    # 先启动frida-server
    print("启动frida-server...")
    return_code, _, _ = run_command("python -m fsm run", verbose=False)
    if return_code != 0:
        print("启动frida-server失败，测试无法继续")
        return False
    
    # 等待frida-server启动
    time.sleep(2)
    
    # 获取运行中的frida-server进程信息
    return_code, stdout, stderr = run_command("python -m fsm ps", verbose=False)
    if return_code != 0 or "No running frida-server processes found" in stdout:
        print("无法获取frida-server进程信息，测试无法继续")
        return False
    
    # 解析PID
    lines = stdout.strip().split('\n')
    pid = None
    for line in lines:
        if line.strip().isdigit() or ' ' in line and line.strip().split()[0].isdigit():
            # 查找包含PID的行
            parts = line.strip().split()
            if parts and parts[0].isdigit():
                pid = parts[0]
                break
    
    if not pid:
        print("无法解析PID，测试无法继续")
        return False
    
    print(f"找到frida-server进程，PID: {pid}")
    
    # 测试按PID杀死进程
    print(f"\n测试按PID杀死进程（PID: {pid}）:")
    return_code, _, _ = run_command(f"python -m fsm kill --pid {pid}")
    if return_code != 0:
        print("按PID杀死进程失败")
        return False
    
    # 验证该进程已被杀死
    print("\n验证该进程已被杀死:")
    return_code, stdout, stderr = run_command("python -m fsm ps", verbose=False)
    if "No running frida-server processes found" in stdout:
        print("验证成功：指定的frida-server进程已被杀死")
    else:
        print("验证失败：指定的frida-server进程可能仍然在运行")
        return False
    
    return True


if __name__ == "__main__":
    # 确保脚本可以被直接执行
    os.chmod(__file__, 0o755)
    
    # 运行测试
    print("===== fsm ps 和 kill 功能测试 =====")
    
    # 测试基本的ps和kill功能
    basic_test_result = test_ps_kill()
    
    # 测试按PID杀死特定进程的功能
    pid_test_result = test_kill_by_pid()
    
    # 总结测试结果
    print("\n===== 测试总结 =====")
    print(f"基本ps和kill功能测试: {'通过' if basic_test_result else '失败'}")
    print(f"按PID杀死特定进程测试: {'通过' if pid_test_result else '失败'}")
    
    if basic_test_result and pid_test_result:
        print("\n所有测试通过！fsm ps和kill功能正常工作。")
        sys.exit(0)
    else:
        print("\n部分测试失败，请检查相关功能。")
        sys.exit(1)