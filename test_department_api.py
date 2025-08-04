#!/usr/bin/env python3
"""
测试部门密钥接口的脚本
使用方法: python test_department_api.py
"""

import requests
import json
import sys

def test_department_api():
    """测试部门密钥接口"""
    
    # 配置
    base_url = "http://localhost:9093"
    api_secret = "your-api-secret"  # 这应该与配置文件中的secret匹配
    
    # 测试用例
    test_cases = [
        {
            "name": "技术部门",
            "secret": "dept001_secret_key",
            "expected_dept": "tech_dept"
        },
        {
            "name": "销售部门", 
            "secret": "dept002_secret_key",
            "expected_dept": "sales_dept"
        },
        {
            "name": "人事部门",
            "secret": "dept003_secret_key", 
            "expected_dept": "hr_dept"
        },
        {
            "name": "财务部门",
            "secret": "dept004_secret_key",
            "expected_dept": "finance_dept"
        },
        {
            "name": "无效密钥",
            "secret": "invalid_secret",
            "expected_dept": None
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {api_secret}",
        "Content-Type": "application/json"
    }
    
    print("开始测试部门密钥接口...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"密钥: {test_case['secret']}")
        
        try:
            # 发送请求
            url = f"{base_url}/department/secret"
            params = {"secret": test_case["secret"]}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"部门ID: {data.get('department_id')}")
                print(f"用户数量: {len(data.get('users', []))}")
                
                # 显示用户信息
                users = data.get('users', [])
                if users:
                    print("用户列表:")
                    for user in users:
                        print(f"  - 用户名: {user.get('username')}")
                        print(f"    密码: {user.get('password')}")
                        print(f"    地区: {user.get('region')}")
                        print()
                else:
                    print("该部门暂无用户")
                    
                # 验证期望结果
                if test_case["expected_dept"] and data.get('department_id') == test_case["expected_dept"]:
                    print("✅ 测试通过")
                elif not test_case["expected_dept"]:
                    print("❌ 应该返回错误，但返回了成功")
                else:
                    print("❌ 部门ID不匹配")
                    
            elif response.status_code == 401:
                if not test_case["expected_dept"]:
                    print("✅ 测试通过 - 正确返回未授权")
                else:
                    print("❌ 意外的未授权错误")
                print(f"错误信息: {response.text}")
                
            else:
                print(f"❌ 意外的状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            print("请确保:")
            print("1. Clash Meta 服务正在运行")
            print("2. 外部控制器已启用 (external-controller: 0.0.0.0:9093)")
            print("3. API密钥配置正确")
            
        print("-" * 30)
    
    print("\n测试完成!")
    print("\n使用说明:")
    print("1. 确保配置文件中包含 department-secrets 配置")
    print("2. 确保规则中包含 PROXY-USER 规则")
    print("3. 接口地址: GET /department/secret?secret=<部门密钥>")
    print("4. 需要在请求头中包含 Authorization: Bearer <api_secret>")

def test_api_connectivity():
    """测试API连接性"""
    base_url = "http://localhost:9093"
    api_secret = "your-api-secret"
    
    headers = {
        "Authorization": f"Bearer {api_secret}",
        "Content-Type": "application/json"
    }
    
    try:
        # 测试基本连接
        response = requests.get(f"{base_url}/", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ API连接正常")
            return True
        else:
            print(f"❌ API连接异常，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到API: {e}")
        return False

if __name__ == "__main__":
    print("Clash Meta 部门密钥接口测试工具")
    print("=" * 50)
    
    # 首先测试连接性
    if test_api_connectivity():
        test_department_api()
    else:
        print("\n请检查:")
        print("1. Clash Meta 是否正在运行")
        print("2. 配置文件中的 external-controller 是否设置为 0.0.0.0:9093")
        print("3. 配置文件中的 secret 是否设置正确")
        sys.exit(1)