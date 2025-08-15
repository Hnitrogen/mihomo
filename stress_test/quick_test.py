#!/usr/bin/env python3
"""
快速测试脚本 - 测试前10个用户凭据
"""

import csv
import requests
import time

def quick_test():
    """快速测试前10个用户"""
    print("🚀 快速测试前10个用户凭据...")
    print("-" * 40)
    
    valid_users = []
    
    try:
        with open('user.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            users = [(row[0].strip(), row[1].strip()) for row in csv_reader if len(row) >= 2][:210]
        
        for i, (username, password) in enumerate(users, 1):
            print(f"测试用户 {i}: {username}...", end=" ")
            
            proxies = {
                'http': f'http://{username}:{password}@192.168.132.58:7891',
                'https': f'http://{username}:{password}@192.168.132.58:7891'
            }
            
            try:
                response = requests.get(
                    'https://www.google.com',
                    proxies=proxies,
                    timeout=5,
                    headers={'User-Agent': 'Quick-Test/1.0'}
                )
                
                if response.status_code == 200:
                    print("✅ 成功")
                    valid_users.append({"username": username, "password": password})
                else:
                    print(f"❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 失败: {str(e)[:30]}...")
            
            time.sleep(0.5)  # 避免请求过快
        
        print("-" * 40)
        print(f"测试完成: {len(valid_users)}/{len(users)} 成功")
        
        if valid_users:
            print("\n有效用户: \n")
            from pprint import pprint 
            pprint(valid_users)
            # for user in valid_users:
            #     print(f"  {user['username']} / {user['password']}")
        
        return valid_users
        
    except FileNotFoundError:
        print("❌ 找不到user.csv文件")
        return []

if __name__ == "__main__":
    quick_test()