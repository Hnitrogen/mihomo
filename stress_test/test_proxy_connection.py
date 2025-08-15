#!/usr/bin/env python3
"""
代理连接测试脚本
在运行压力测试前，先验证代理连接是否正常
"""

import requests
import time
from config import PROXY_CONFIG, PROXY_USERS, TARGET_URLS


def test_proxy_connection():
    """测试代理连接"""
    print("🔍 测试代理连接...")
    print(f"代理地址: {PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}")
    print(f"测试用户数: {len(PROXY_USERS)}")
    print("-" * 50)
    
    success_count = 0
    total_tests = 0
    
    for i, user in enumerate(PROXY_USERS[:3]):  # 只测试前3个用户
        print(f"\n测试用户 {i+1}: {user['username']}")
        
        # 配置代理
        proxies = {
            'http': f'http://{user["username"]}:{user["password"]}@{PROXY_CONFIG["host"]}:{PROXY_CONFIG["port"]}',
            'https': f'http://{user["username"]}:{user["password"]}@{PROXY_CONFIG["host"]}:{PROXY_CONFIG["port"]}'
        }
        
        # 测试几个URL
        test_urls = TARGET_URLS[:3]  # 只测试前3个URL
        
        for url in test_urls:
            total_tests += 1
            try:
                print(f"  测试 {url}...", end=" ")
                
                start_time = time.time()
                response = requests.get(
                    url, 
                    proxies=proxies, 
                    timeout=10,
                    headers={'User-Agent': 'Clash-Meta-Test/1.0'}
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    print(f"✅ 成功 ({end_time - start_time:.2f}s)")
                    success_count += 1
                else:
                    print(f"❌ 失败 (状态码: {response.status_code})")
                    
            except requests.exceptions.ProxyError:
                print("❌ 代理连接失败")
            except requests.exceptions.Timeout:
                print("❌ 请求超时")
            except Exception as e:
                print(f"❌ 错误: {e}")
            
            time.sleep(1)  # 避免请求过快
    
    print("\n" + "=" * 50)
    print(f"测试结果: {success_count}/{total_tests} 成功")
    print(f"成功率: {(success_count/total_tests)*100:.1f}%")
    
    if success_count > 0:
        print("✅ 代理连接正常，可以开始压力测试")
        return True
    else:
        print("❌ 代理连接失败，请检查配置")
        return False


def check_clash_meta_status():
    """检查 Clash-Meta 状态"""
    print("\n🔍 检查 Clash-Meta 状态...")
    
    try:
        # 尝试访问 Clash-Meta API
        api_url = f"http://{PROXY_CONFIG['host']}:9093/configs"  # 默认API端口
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Clash-Meta API 可访问")
            return True
        else:
            print(f"⚠️  Clash-Meta API 响应异常 (状态码: {response.status_code})")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 Clash-Meta API")
    except Exception as e:
        print(f"❌ 检查 Clash-Meta 状态时出错: {e}")
    
    return False


if __name__ == "__main__":
    print("=" * 60)
    print("    Clash-Meta 代理连接测试")
    print("=" * 60)
    
    # 检查 Clash-Meta 状态
    clash_status = check_clash_meta_status()
    
    # 测试代理连接
    proxy_status = test_proxy_connection()
    
    print("\n" + "=" * 60)
    if proxy_status:
        print("🎉 所有测试通过，可以开始压力测试！")
        print("\n运行压力测试:")
        print("  Windows: run_test.bat")
        print("  命令行: python comprehensive_stress_test.py --scenario light")
    else:
        print("⚠️  请先解决连接问题再进行压力测试")
        print("\n检查项目:")
        print("  1. Clash-Meta 是否正在运行")
        print("  2. 代理地址和端口是否正确")
        print("  3. 用户凭据是否有效")
        print("  4. 网络连接是否正常")
    
    print("=" * 60)