#!/usr/bin/env python3
import requests
import json

# curl.exe -H "Authorization: Bearer your-api-secret" "http://localhost:9093/department/secret?secret=dept001_secret_key"
def make_correct_request():
    """展示正确的请求方式"""
    
    # 配置
    base_url = "http://localhost:9093"
    api_secret = "seo-pinkman"  # 必须与配置文件中的secret匹配
    dept_secret = "tech_dept"  # 必须在department-secrets中存在
    
    # 请求头 - API认证
    headers = {
        "Authorization": f"Bearer {api_secret}",
        "Content-Type": "application/json"
    }
    
    # 查询参数 - 部门密钥
    params = {
        "secret": dept_secret
    }
    
    print("发送正确的请求...")
    print(f"URL: {base_url}/department/secret")
    print(f"Headers: {headers}")
    print(f"Params: {params}")
    print("-" * 50)
    
    try:
        response = requests.get(
            f"{base_url}/department/secret",
            headers=headers,
            params=params,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 请求成功!")
            print(f"部门ID: {data['department_id']}")
            print(f"用户数量: {len(data['users'])}")
            print("\n用户列表:")
            for user in data['users']:
                print(f"  - {user['username']}: {user['region']}")
        else:
            print("❌ 请求失败!")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")

if __name__ == "__main__":
    make_correct_request()