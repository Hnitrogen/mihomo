#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash 订阅文件聚合器
功能：
1. 聚合多个Clash配置文件的proxies
2. 为每个代理生成随机用户认证规则
3. 保留原有的PROXY-USER规则
4. 生成标准的路由规则
"""

import yaml
import random
import string
import argparse
import os
from typing import List, Dict, Any
from collections import OrderedDict


class ClashAggregator:
    def __init__(self):
        self.aggregated_proxies = []
        self.existing_proxy_users = set()
        self.generated_users = []
        self.proxy_groups = []
        
    def generate_random_credentials(self, username_length=8):
        """生成随机用户名和密码，密码长度是用户名长度的两倍"""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
        password_length = username_length * 2
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=password_length))
        return username, password
    
    def load_yaml_file(self, file_path: str) -> Dict[Any, Any]:
        """加载YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"警告: 无法加载文件 {file_path}: {e}")
            return {}
    
    def extract_proxies(self, config: Dict[Any, Any]) -> List[Dict[Any, Any]]:
        """从配置中提取代理"""
        return config.get('proxies', [])
    
    def extract_existing_proxy_user_rules(self, config: Dict[Any, Any]) -> List[str]:
        """提取现有的PROXY-USER规则"""
        rules = config.get('rules', [])
        proxy_user_rules = []
        
        for rule in rules:
            if isinstance(rule, str) and rule.startswith('PROXY-USER,'):
                proxy_user_rules.append(rule)
                # 提取用户名以避免重复
                parts = rule.split(',')
                if len(parts) >= 2:
                    username = parts[1]
                    self.existing_proxy_users.add(username)
        
        return proxy_user_rules
    
    def aggregate_files(self, file_paths: List[str]):
        """聚合多个配置文件"""
        existing_proxy_user_rules = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"警告: 文件不存在 {file_path}")
                continue
                
            print(f"处理文件: {file_path}")
            config = self.load_yaml_file(file_path)
            
            # 提取代理
            proxies = self.extract_proxies(config)
            self.aggregated_proxies.extend(proxies)
            print(f"  - 提取到 {len(proxies)} 个代理")
            
            # 提取现有的PROXY-USER规则
            proxy_user_rules = self.extract_existing_proxy_user_rules(config)
            existing_proxy_user_rules.extend(proxy_user_rules)
            print(f"  - 提取到 {len(proxy_user_rules)} 个PROXY-USER规则")
        
        print(f"\n总计聚合了 {len(self.aggregated_proxies)} 个代理")
        return existing_proxy_user_rules
    
    def generate_user_rules_for_proxies(self) -> List[str]:
        """为每个代理生成用户认证规则"""
        user_rules = []
        
        for i, proxy in enumerate(self.aggregated_proxies):
            proxy_name = proxy.get('name', f'proxy_{i}')
            
            # 生成唯一的用户名
            while True:
                username, password = self.generate_random_credentials()
                if username not in self.existing_proxy_users:
                    self.existing_proxy_users.add(username)
                    break
            
            # 直接匹配到具体的代理名称
            rule = f"PROXY-USER,{username},{proxy_name}"
            user_rules.append(rule)
            
            self.generated_users.append({
                'username': username,
                'password': password,
                'proxy_name': proxy_name,
                'target_proxy': proxy_name
            })
        
        return user_rules
    
    def create_base_config(self) -> Dict[Any, Any]:
        """创建基础配置"""
        return {
            'mixed-port': 7891,
            'allow-lan': True,
            'external-controller': '0.0.0.0:9093',
            'bind-address': '*',
            'mode': 'rule',
            'log-level': 'info',
            'ipv6': False,
            'profile': {
                'store-selected': True,
                'tracing': False,
                'store-fake-ip': False
            },
            'unified-delay': True,
            'dns': {
                'enable': True,
                'ipv6': False,
                'listen': '0.0.0.0:1053',
                'enhanced-mode': 'fake-ip',
                'fake-ip-range': '198.18.0.1/16',
                'use-hosts': True,
                'default-nameserver': ['223.5.5.5'],
                'nameserver': ['https://doh.pub/dns-query', 'https://dns.alidns.com/dns-query'],
                'fake-ip-filter': ['*.lan', 'localhost.ptlogin2.qq.com', 'dns.msftncsi.com'],
                'fallback': ['1.1.1.1', '8.8.8.8'],
                'fallback-filter': {'geoip': True, 'geoip-code': 'CN', 'ipcidr': ['240.0.0.0/4']}
            }
        }
    

    
    def create_authentication_config(self) -> List[str]:
        """创建认证配置"""
        auth_list = []
        for user in self.generated_users:
            auth_list.append(f"{user['username']}:{user['password']}")
        return auth_list
    
    def generate_aggregated_config(self, existing_proxy_user_rules: List[str], output_file: str):
        """生成聚合后的配置文件"""
        config = self.create_base_config()
        
        # 添加代理
        config['proxies'] = self.aggregated_proxies
        
        # 生成新的用户规则
        new_user_rules = self.generate_user_rules_for_proxies()
        
        # 添加认证配置
        config['authentication'] = self.create_authentication_config()
        
        # 构建规则列表
        rules = []
        
        # 添加基于代理用户认证的路由规则 - 必须放在最前面
        if new_user_rules:
            rules.append("# 基于代理用户认证的路由规则 - 必须放在最前面")
            rules.extend(new_user_rules)
        
        # 添加现有的PROXY-USER规则
        if existing_proxy_user_rules:
            rules.extend(existing_proxy_user_rules)
        
        # 添加固定的测试和默认规则
        default_proxy = self.aggregated_proxies[0].get('name', 'DIRECT') if self.aggregated_proxies else 'DIRECT'
        rules.extend([
            "# 测试域名",
            f"DOMAIN-SUFFIX,httpbin.org,{default_proxy}",
            f"DOMAIN-SUFFIX,google.com,{default_proxy}",
            "# 本地直连", 
            "IP-CIDR,127.0.0.0/8,DIRECT",
            "IP-CIDR,192.168.0.0/16,DIRECT",
            "IP-CIDR,10.0.0.0/8,DIRECT",
            "# 默认规则",
            f"MATCH,{default_proxy}"
        ])
        
        config['rules'] = rules
        
        # 保存配置文件
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"\n聚合配置已保存到: {output_file}")
        
        # 保存用户凭据信息
        credentials_file = output_file.replace('.yaml', '_credentials.txt').replace('.yml', '_credentials.txt')
        with open(credentials_file, 'w', encoding='utf-8') as f:
            f.write("生成的用户凭据信息 (直接匹配代理订阅):\n")
            f.write("=" * 60 + "\n")
            for user in self.generated_users:
                f.write(f"用户名: {user['username']}\n")
                f.write(f"密码: {user['password']}\n") 
                f.write(f"直接匹配代理: {user['proxy_name']}\n")
                f.write(f"规则: PROXY-USER,{user['username']},{user['proxy_name']}\n")
                f.write("-" * 40 + "\n")
        
        print(f"用户凭据信息已保存到: {credentials_file}")


def main():
    parser = argparse.ArgumentParser(description='Clash 订阅文件聚合器')
    parser.add_argument('files', nargs='+', help='要聚合的Clash配置文件路径')
    parser.add_argument('-o', '--output', default='aggregated_clash_config.yaml', 
                       help='输出文件名 (默认: aggregated_clash_config.yaml)')
    
    args = parser.parse_args()
    
    aggregator = ClashAggregator()
    
    print("开始聚合Clash配置文件...")
    print(f"输入文件: {', '.join(args.files)}")
    print(f"输出文件: {args.output}")
    print("-" * 50)
    
    # 聚合文件
    existing_proxy_user_rules = aggregator.aggregate_files(args.files)
    
    # 生成聚合配置
    aggregator.generate_aggregated_config(existing_proxy_user_rules, args.output)
    
    print(f"\n聚合完成!")
    print(f"- 总代理数量: {len(aggregator.aggregated_proxies)}")
    print(f"- 生成用户数量: {len(aggregator.generated_users)}")
    print(f"- 保留现有规则: {len(existing_proxy_user_rules)}")


if __name__ == '__main__':
    main()