#!/usr/bin/env python3
"""
用户凭据验证脚本
读取user.csv文件，测试每个账号的代理连接，输出有效的用户凭据
"""

import csv
import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 代理配置
PROXY_HOST = "192.168.132.58"
PROXY_PORT = "7891"
TEST_URL = "https://www.google.com"
TIMEOUT = 10
MAX_WORKERS = 10  # 并发测试数量

# 线程锁用于安全输出
print_lock = threading.Lock()
valid_users = []
valid_users_lock = threading.Lock()


def test_proxy_user(username, password):
    """测试单个用户的代理连接"""
    proxies = {
        'http': f'http://{username}:{password}@{PROXY_HOST}:{PROXY_PORT}',
        'https': f'http://{username}:{password}@{PROXY_HOST}:{PROXY_PORT}'
    }
    
    try:
        response = requests.get(
            TEST_URL,
            proxies=proxies,
            timeout=TIMEOUT,
            headers={'User-Agent': 'Clash-Meta-Validator/1.0'}
        )
        
        if response.status_code == 200:
            with print_lock:
                print(f"✅ {username} - 连接成功")
            
            with valid_users_lock:
                valid_users.append({
                    "username": username,
                    "password": password
                })
            return True
        else:
            with print_lock:
                print(f"❌ {username} - HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ProxyError:
        with print_lock:
            print(f"❌ {username} - 代理连接失败")
        return False
    except requests.exceptions.Timeout:
        with print_lock:
            print(f"❌ {username} - 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        with print_lock:
            print(f"❌ {username} - 连接错误")
        return False
    except Exception as e:
        with print_lock:
            print(f"❌ {username} - 未知错误: {e}")
        return False


def read_users_from_csv(csv_file):
    """从CSV文件读取用户凭据"""
    users = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row_num, row in enumerate(csv_reader, 1):
                if len(row) >= 2:
                    username = row[0].strip()
                    password = row[1].strip()
                    if username and password:
                        users.append((username, password))
                else:
                    print(f"⚠️  第{row_num}行格式错误，跳过: {row}")
        
        print(f"📋 从CSV文件读取到 {len(users)} 个用户凭据")
        return users
        
    except FileNotFoundError:
        print(f"❌ 文件未找到: {csv_file}")
        return []
    except Exception as e:
        print(f"❌ 读取CSV文件时出错: {e}")
        return []


def validate_all_users(csv_file):
    """验证所有用户凭据"""
    print("=" * 60)
    print("    Clash-Meta 用户凭据验证工具")
    print("=" * 60)
    print(f"代理地址: {PROXY_HOST}:{PROXY_PORT}")
    print(f"测试URL: {TEST_URL}")
    print(f"并发数: {MAX_WORKERS}")
    print("-" * 60)
    
    # 读取用户列表
    users = read_users_from_csv(csv_file)
    if not users:
        return []
    
    print(f"开始验证 {len(users)} 个用户...")
    print("-" * 60)
    
    # 并发测试用户
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务
        future_to_user = {
            executor.submit(test_proxy_user, username, password): (username, password)
            for username, password in users
        }
        
        # 处理完成的任务
        completed = 0
        for future in as_completed(future_to_user):
            completed += 1
            username, password = future_to_user[future]
            
            # 显示进度
            if completed % 10 == 0 or completed == len(users):
                with print_lock:
                    print(f"进度: {completed}/{len(users)} ({completed/len(users)*100:.1f}%)")
            
            # 添加小延迟避免过于频繁的请求
            time.sleep(0.1)
    
    end_time = time.time()
    
    # 输出结果
    print("\n" + "=" * 60)
    print("验证完成！")
    print(f"总用户数: {len(users)}")
    print(f"有效用户数: {len(valid_users)}")
    print(f"成功率: {len(valid_users)/len(users)*100:.1f}%")
    print(f"耗时: {end_time - start_time:.2f}秒")
    print("=" * 60)
    
    return valid_users


def generate_config_output(valid_users):
    """生成配置文件格式的输出"""
    if not valid_users:
        print("❌ 没有有效的用户凭据")
        return
    
    print("\n# 代理用户凭据 - 从实际凭据文件中提取")
    print("PROXY_USERS = [")
    
    for i, user in enumerate(valid_users):
        comma = "," if i < len(valid_users) - 1 else ""
        print(f'    {{"username": "{user["username"]}", "password": "{user["password"]}"}}{comma}')
    
    print("]")
    
    # 保存到文件
    output_file = "valid_users_config.py"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 验证通过的代理用户凭据\n")
            f.write("# 生成时间: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            f.write("PROXY_USERS = [\n")
            
            for i, user in enumerate(valid_users):
                comma = "," if i < len(valid_users) - 1 else ""
                f.write(f'    {{"username": "{user["username"]}", "password": "{user["password"]}"}}{comma}\n')
            
            f.write("]\n")
        
        print(f"\n✅ 有效用户凭据已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 保存配置文件时出错: {e}")


def main():
    csv_file = "user.csv"
    
    # 检查CSV文件是否存在
    try:
        with open(csv_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"❌ 找不到文件: {csv_file}")
        print("请确保user.csv文件在当前目录中")
        return
    
    # 验证所有用户
    valid_users_list = validate_all_users(csv_file)
    
    # 生成配置输出
    if valid_users_list:
        generate_config_output(valid_users_list)
        
        # 显示前几个有效用户作为示例
        print(f"\n📋 前5个有效用户示例:")
        for i, user in enumerate(valid_users_list[:5]):
            print(f"  {i+1}. {user['username']} / {user['password']}")
        
        if len(valid_users_list) > 5:
            print(f"  ... 还有 {len(valid_users_list) - 5} 个用户")
    else:
        print("\n❌ 没有找到有效的用户凭据")
        print("请检查:")
        print("  1. Clash-Meta 是否正在运行")
        print("  2. 代理地址和端口是否正确")
        print("  3. 网络连接是否正常")
        print("  4. 用户凭据是否过期")


if __name__ == "__main__":
    main()