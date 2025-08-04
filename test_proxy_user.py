#!/usr/bin/env python3
"""
测试脚本：验证基于代理认证用户名的路由功能
"""

import requests
import subprocess
import time
import json

def test_curl_proxy_user():
    """使用 curl 测试不同用户的代理路由"""
    
    print("=== 测试基于代理认证用户名的路由 ===\n")
    
    # 测试用例
    test_cases = [
        {
            "name": "VIP用户 feifeimao",
            "user": "feifeimao",
            "password": "7212",
            "expected": "应该走美国代理 (US-01)"
        },
        {
            "name": "VIP用户 vipuser", 
            "user": "vipuser",
            "password": "7212",
            "expected": "应该走美国代理 (US-01)"
        },
        {
            "name": "普通用户 normaluser",
            "user": "normaluser", 
            "password": "7212",
            "expected": "应该走香港代理 (HK-01)"
        }
    ]
    
    for case in test_cases:
        print(f"测试: {case['name']}")
        print(f"预期: {case['expected']}")
        
        # 使用 curl 命令测试
        cmd = [
            "curl", 
            "--proxy-user", f"{case['user']}:{case['password']}",
            "--proxy", "http://127.0.0.1:7891",
            "http://httpbin.org/ip",
            "-s"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    ip = response.get('origin', 'Unknown')
                    print(f"结果: IP = {ip}")
                except json.JSONDecodeError:
                    print(f"结果: {result.stdout}")
            else:
                print(f"错误: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("错误: 请求超时")
        except Exception as e:
            print(f"错误: {e}")
        
        print("-" * 50)
        time.sleep(1)

def test_python_requests():
    """使用 Python requests 测试代理路由"""
    
    print("\n=== 使用 Python requests 测试 ===\n")
    
    test_cases = [
        ("feifeimao", "7212", "VIP用户"),
        ("normaluser", "7212", "普通用户")
    ]
    
    for user, password, desc in test_cases:
        print(f"测试: {desc} ({user})")
        
        proxies = {
            'http': f'http://{user}:{password}@127.0.0.1:7891',
            'https': f'http://{user}:{password}@127.0.0.1:7891'
        }
        
        try:
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
            if response.status_code == 200:
                data = response.json()
                ip = data.get('origin', 'Unknown')
                print(f"结果: IP = {ip}")
            else:
                print(f"错误: HTTP {response.status_code}")
        except Exception as e:
            print(f"错误: {e}")
        
        print("-" * 50)
        time.sleep(1)

if __name__ == "__main__":
    print("请确保 clash-meta 正在运行并使用 proxy_user_config.yaml 配置")
    print("按 Enter 继续...")
    input()
    
    test_curl_proxy_user()
    test_python_requests()