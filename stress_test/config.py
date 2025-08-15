#!/usr/bin/env python3
"""
压力测试配置文件
"""

# Clash-Meta 代理配置
PROXY_CONFIG = {
    'host': '192.168.132.58',  # 根据实际情况修改
    'port': 7891,
    'timeout': 30
}

# 测试目标URL配置
TARGET_URLS = [
    # 基础测试URL
    "https://www.google.com",
    "https://httpbin.org/get",
    "https://httpbin.org/ip",
    "https://httpbin.org/user-agent",
    
    # GitHub相关
    "https://www.github.com",
    "https://api.github.com",
    
    # 技术网站
    "https://www.stackoverflow.com",
    
    # 延迟测试
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/2",
    
    # 状态码测试
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/201",
    
    # JSON API测试
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/users/1",
    
    # 大文件下载测试 (小心使用)
    # "https://httpbin.org/bytes/1024",
    # "https://httpbin.org/bytes/10240",
]

# 代理用户凭据 - 从user.csv验证后的有效用户
# 运行 python validate_users.py 来生成有效的用户列表
try:
    from valid_users_config import PROXY_USERS
    print(f"✅ 已加载 {len(PROXY_USERS)} 个验证通过的用户凭据")
except ImportError:
    # 如果没有验证文件，使用默认的测试用户
    print("⚠️  未找到验证文件，使用默认测试用户")
    print("请运行 'python validate_users.py' 来验证user.csv中的用户")
    PROXY_USERS = [
        {"username": "dp1_n6p5iypo", "password": "lIdIpNDSLKfWBaPp"},
        {"username": "dp1_j6xaudjt", "password": "MdmQRf7aHtvMZBsv"},
        {"username": "dp1_v9abt0zb", "password": "RDh0J8UMjA7ti1fu"},
        {"username": "dp1_v66t8aol", "password": "Z0EWTKPQqlxXQiHi"},
        # 这些是示例用户，请运行验证脚本获取真实有效用户
    ]

# 测试场景配置
TEST_SCENARIOS = {
    'light': {
        'users': 10,
        'spawn_rate': 2,
        'duration': '5m'
    },
    'medium': {
        'users': 50,
        'spawn_rate': 5,
        'duration': '10m'
    },
    'heavy': {
        'users': 100,
        'spawn_rate': 10,
        'duration': '15m'
    },
    'extreme': {
        'users': 200,
        'spawn_rate': 20,
        'duration': '20m'
    }
}

# 监控配置
MONITORING_CONFIG = {
    'interval': 5,  # 监控间隔(秒)
    'save_interval': 60,  # 保存间隔(秒)
    'process_names': ['mihomo', 'clash-meta', 'clash']  # 要监控的进程名
}

# 报告配置
REPORT_CONFIG = {
    'output_dir': 'reports',
    'include_charts': True,
    'chart_types': ['response_time', 'rps', 'system_resources']
}