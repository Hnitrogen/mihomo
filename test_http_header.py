#!/usr/bin/env python3
"""
测试 HTTP-HEADER 规则的脚本
"""
import requests
import time

# 代理配置
proxy_url = "http://127.0.0.1:7891"
proxies = {
    'http': proxy_url,
    'https': proxy_url
}

def test_request(headers=None, description=""):
    """发送测试请求"""
    print(f"\n=== {description} ===")
    try:
        response = requests.get(
            'http://httpbin.org/headers',
            headers=headers,
            proxies=proxies,
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return True
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def main():
    print("开始测试 HTTP-HEADER 规则...")
    
    # 测试1: 不带特殊请求头
    test_request(description="普通请求（无特殊请求头）")
    
    time.sleep(2)
    
    # 测试2: 带有 VIP 用户请求头
    vip_headers = {
        'proxy_user_id': 'vip_user',
        'User-Agent': 'TestClient/1.0'
    }
    test_request(vip_headers, "VIP 用户请求")
    
    time.sleep(2)
    
    # 测试3: 带有 Premium 用户请求头
    premium_headers = {
        'proxy_user_id': 'premium_user',
        'User-Agent': 'TestClient/1.0'
    }
    test_request(premium_headers, "Premium 用户请求")
    
    time.sleep(2)
    
    # 测试4: 带有普通用户请求头
    normal_headers = {
        'proxy_user_id': 'normal_user',
        'User-Agent': 'TestClient/1.0'
    }
    test_request(normal_headers, "普通用户请求")

if __name__ == "__main__":
    main()