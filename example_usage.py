#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash 聚合器使用示例
"""

from clash_aggregator import ClashAggregator
import os

def example_usage():
    """示例用法"""
    
    # 创建聚合器实例
    aggregator = ClashAggregator()
    
    # 要聚合的配置文件列表
    config_files = [
        'nicai.yaml',
        'nicai_simple.yaml'
        # 可以添加更多配置文件
    ]
    
    # 检查文件是否存在
    existing_files = [f for f in config_files if os.path.exists(f)]
    
    if not existing_files:
        print("错误: 没有找到可用的配置文件")
        print("请确保以下文件存在:")
        for f in config_files:
            print(f"  - {f}")
        return
    
    print("找到以下配置文件:")
    for f in existing_files:
        print(f"  - {f}")
    
    print("\n开始聚合...")
    
    # 聚合文件
    existing_proxy_user_rules = aggregator.aggregate_files(existing_files)
    
    # 生成聚合配置
    output_file = 'aggregated_clash_config.yaml'
    aggregator.generate_aggregated_config(existing_proxy_user_rules, output_file)
    
    print(f"\n聚合完成!")
    print(f"- 输出文件: {output_file}")
    print(f"- 总代理数量: {len(aggregator.aggregated_proxies)}")
    print(f"- 生成用户数量: {len(aggregator.generated_users)}")
    print(f"- 保留现有规则: {len(existing_proxy_user_rules)}")
    
    # 显示生成的用户信息
    if aggregator.generated_users:
        print(f"\n生成的用户凭据 (前5个):")
        for i, user in enumerate(aggregator.generated_users[:5]):
            print(f"  {i+1}. 用户名: {user['username']}, 密码: {user['password']}, 组: {user['proxy_group']}")
        
        if len(aggregator.generated_users) > 5:
            print(f"  ... 还有 {len(aggregator.generated_users) - 5} 个用户")

if __name__ == '__main__':
    example_usage()