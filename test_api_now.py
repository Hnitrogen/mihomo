#!/usr/bin/env python3
import requests
import json

def test_department_api():
    base_url = "http://localhost:9093"
    api_secret = "your-api-secret"
    
    headers = {
        "Authorization": f"Bearer {api_secret}",
        "Content-Type": "application/json"
    }
    
    print("测试部门密钥接口...")
    print("=" * 50)
    
    # 测试技术部门
    print("\n1. 测试技术部门 (dept001_secret_key)")
    try:
        response = requests.get(
            f"{base_url}/department/secret",
            headers=headers,
            params={"secret": "dept001_secret_key"},
            timeout=5
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"部门ID: {data.get('department_id')}")
            print(f"用户数量: {len(data.get('users', []))}")
            print("用户详情:")
            for user in data.get('users', []):
                print(f"  - 用户名: {user.get('username')}")
                print(f"    密码: {user.get('password')}")
                print(f"    地区: {user.get('region')}")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试销售部门
    print("\n2. 测试销售部门 (dept002_secret_key)")
    try:
        response = requests.get(
            f"{base_url}/department/secret",
            headers=headers,
            params={"secret": "dept002_secret_key"},
            timeout=5
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"部门ID: {data.get('department_id')}")
            print(f"用户数量: {len(data.get('users', []))}")
            for user in data.get('users', []):
                print(f"  - {user.get('username')}: {user.get('region')}")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试无效密钥
    print("\n3. 测试无效密钥")
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