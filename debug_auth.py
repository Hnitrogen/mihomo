#!/usr/bin/env python3
import requests

def test_auth():
    base_url = "http://localhost:9093"
    
    print("测试API认证...")
    
    # 1. 测试不带认证头的请求
    print("\n1. 不带认证头的请求:")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试错误的API密钥
    print("\n2. 错误的API密钥:")
    headers = {"Authorization": "Bearer wrong-secret"}
    try:
        response = requests.get(f"{base_url}/", headers=headers, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试正确的API密钥
    print("\n3. 正确的API密钥:")
    headers = {"Authorization": "Bearer your-api-secret"}
    try:
        response = requests.get(f"{base_url}/", headers=headers, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 4. 测试部门接口 - 正确的API密钥但错误的部门密钥
    print("\n4. 部门接口 - 错误的部门密钥:")
    try:
        response = requests.get(
            f"{base_url}/department/secret",
            headers=headers,
            params={"secret": "wrong_dept_secret"},
            timeout=5
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 5. 测试部门接口 - 正确的密钥
    print("\n5. 部门接口 - 正确的部门密钥:")
    try:
        response = requests.get(
            f"{base_url}/department/secret",
            headers=headers,
            params={"secret": "dept001_secret_key"},
            timeout=5
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 请求成功!")
        else:
            print(f"❌ 请求失败: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_auth()