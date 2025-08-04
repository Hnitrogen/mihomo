#!/usr/bin/env python3
"""
简单的部门密钥接口测试脚本
"""

import requests
import json

def test_department_api():
    base_url = "http://localhost:9093"
    api_secret = "test-secret-123"
    
    headers = {
        "Authorization": f"Bearer {api_secret}",
        "Content-Type": "application/json"
    }
    
    # 测试技术部门
    print("测试技术部门...")
    try:
        response = requests.get(
            f"{base_url}/department/secret",
            headers=headers,
            params={"secret": "tech_secret_123"},
            timeout=5
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

    # 测试无效密钥
    print("\n测试无效密钥...")
    try:
        response = requests.get(
            f"{base_url}/department/secret",
            headers=headers,
            params={"secret": "invalid_secret"},
            timeout=5
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_department_api()