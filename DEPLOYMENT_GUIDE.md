# Clash-Meta 代理用户路由部署指南

## 快速开始

### 1. 编译项目

```bash
# 克隆项目（如果还没有）
git clone https://github.com/MetaCubeX/mihomo.git
cd mihomo

# 应用我们的修改后编译
go build -o mihomo-custom.exe .
```

### 2. 验证实现

```bash
# 运行验证脚本
go run verify_implementation.go
```

预期输出：
```
=== 验证 PROXY-USER 规则实现 ===

1. 测试规则创建...
✓ 规则创建成功: feifeimao/vipuser -> VIP_PROXY

2. 测试规则类型...
✓ 规则类型正确: ProxyUser

3. 测试规则匹配...
✓ VIP用户 feifeimao: 用户='feifeimao', 匹配=true, 适配器='VIP_PROXY'
✓ VIP用户 vipuser: 用户='vipuser', 匹配=true, 适配器='VIP_PROXY'
✗ 普通用户 normaluser: 用户='normaluser', 匹配=false, 适配器=''
✗ 空用户名: 用户='', 匹配=false, 适配器=''

4. 测试规则解析...
✓ 规则解析成功: testuser -> TEST_PROXY

5. 测试多用户解析...
✓ 用户 'user1': 匹配=true
✓ 用户 'user2': 匹配=true
✓ 用户 'user3': 匹配=true
✗ 用户 'user4': 匹配=false

=== 所有测试通过! ===
```

### 3. 启动服务

```bash
# 使用测试配置启动
mihomo-custom.exe -f proxy_user_config.yaml

# 或使用生产配置
mihomo-custom.exe -f example_production_config.yaml
```

### 4. 测试功能

```bash
# 运行Python测试脚本
python test_proxy_user.py

# 或手动测试
curl --proxy-user feifeimao:7212 --proxy http://127.0.0.1:7891 http://httpbin.org/ip
```

## 生产环境部署

### 1. 系统要求

- Windows 10/11 或 Windows Server 2016+
- Go 1.19+ (编译时需要)
- 至少 512MB RAM
- 网络连接

### 2. 服务化部署

创建 Windows 服务配置文件 `mihomo-service.xml`：

```xml
<service>
    <id>mihomo-proxy</id>
    <name>Mihomo Proxy Service</name>
    <description>Mihomo代理服务，支持用户路由</description>
    <executable>C:\mihomo\mihomo-custom.exe</executable>
    <arguments>-f C:\mihomo\config.yaml</arguments>
    <workingdirectory>C:\mihomo</workingdirectory>
    <logmode>rotate</logmode>
    <depend></depend>
    <startmode>Automatic</startmode>
    <delayedAutoStart>true</delayedAutoStart>
</service>
```

使用 WinSW 安装服务：
```bash
# 下载 WinSW
# 将 mihomo-custom.exe 和配置文件放到 C:\mihomo\
# 安装服务
winsw install mihomo-service.xml

# 启动服务
net start mihomo-proxy
```

### 3. 配置管理

创建配置管理脚本 `config_manager.py`：

```python
#!/usr/bin/env python3
"""
配置管理工具
"""

import yaml
import json
import argparse
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self):
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
    
    def add_user_rule(self, users, proxy_group):
        """添加用户路由规则"""
        rule = f'PROXY-USER,{users},{proxy_group}'
        
        if 'rules' not in self.config:
            self.config['rules'] = []
        
        # 插入到规则列表开头（高优先级）
        self.config['rules'].insert(0, rule)
        print(f"已添加规则: {rule}")
    
    def remove_user_rule(self, users):
        """删除用户路由规则"""
        if 'rules' not in self.config:
            return
        
        rules_to_remove = []
        for i, rule in enumerate(self.config['rules']):
            if isinstance(rule, str) and rule.startswith('PROXY-USER'):
                parts = rule.split(',')
                if len(parts) >= 2 and parts[1] == users:
                    rules_to_remove.append(i)
        
        # 从后往前删除，避免索引变化
        for i in reversed(rules_to_remove):
            removed_rule = self.config['rules'].pop(i)
            print(f"已删除规则: {removed_rule}")
    
    def list_user_rules(self):
        """列出所有用户路由规则"""
        if 'rules' not in self.config:
            return []
        
        user_rules = []
        for rule in self.config['rules']:
            if isinstance(rule, str) and rule.startswith('PROXY-USER'):
                user_rules.append(rule)
        
        return user_rules
    
    def add_proxy_group(self, name, group_type, proxies):
        """添加代理组"""
        if 'proxy-groups' not in self.config:
            self.config['proxy-groups'] = []
        
        group = {
            'name': name,
            'type': group_type,
            'proxies': proxies
        }
        
        self.config['proxy-groups'].append(group)
        print(f"已添加代理组: {name}")

def main():
    parser = argparse.ArgumentParser(description='Mihomo配置管理工具')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加用户规则
    add_parser = subparsers.add_parser('add-user', help='添加用户路由规则')
    add_parser.add_argument('users', help='用户名，多个用户用/分隔')
    add_parser.add_argument('proxy_group', help='代理组名称')
    
    # 删除用户规则
    remove_parser = subparsers.add_parser('remove-user', help='删除用户路由规则')
    remove_parser.add_argument('users', help='用户名')
    
    # 列出用户规则
    list_parser = subparsers.add_parser('list-users', help='列出所有用户路由规则')
    
    # 添加代理组
    group_parser = subparsers.add_parser('add-group', help='添加代理组')
    group_parser.add_argument('name', help='代理组名称')
    group_parser.add_argument('type', help='代理组类型')
    group_parser.add_argument('proxies', nargs='+', help='代理列表')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = ConfigManager(args.config)
    
    if args.command == 'add-user':
        manager.add_user_rule(args.users, args.proxy_group)
        manager.save_config()
    
    elif args.command == 'remove-user':
        manager.remove_user_rule(args.users)
        manager.save_config()
    
    elif args.command == 'list-users':
        rules = manager.list_user_rules()
        if rules:
            print("当前用户路由规则:")
            for rule in rules:
                print(f"  {rule}")
        else:
            print("没有找到用户路由规则")
    
    elif args.command == 'add-group':
        manager.add_proxy_group(args.name, args.type, args.proxies)
        manager.save_config()

if __name__ == '__main__':
    main()
```

### 4. 监控和日志

创建监控脚本 `monitor.py`：

```python
#!/usr/bin/env python3
"""
Mihomo服务监控脚本
"""

import requests
import time
import json
from datetime import datetime

class MihomoMonitor:
    def __init__(self, api_url="http://127.0.0.1:9093", secret=None):
        self.api_url = api_url.rstrip('/')
        self.headers = {}
        if secret:
            self.headers['Authorization'] = f'Bearer {secret}'
    
    def get_traffic_info(self):
        """获取流量信息"""
        try:
            response = requests.get(f"{self.api_url}/traffic", headers=self.headers)
            return response.json()
        except Exception as e:
            print(f"获取流量信息失败: {e}")
            return None
    
    def get_connections(self):
        """获取连接信息"""
        try:
            response = requests.get(f"{self.api_url}/connections", headers=self.headers)
            return response.json()
        except Exception as e:
            print(f"获取连接信息失败: {e}")
            return None
    
    def get_proxies(self):
        """获取代理信息"""
        try:
            response = requests.get(f"{self.api_url}/proxies", headers=self.headers)
            return response.json()
        except Exception as e:
            print(f"获取代理信息失败: {e}")
            return None
    
    def monitor_loop(self, interval=30):
        """监控循环"""
        print(f"开始监控 Mihomo 服务 (间隔: {interval}秒)")
        print("=" * 60)
        
        while True:
            try:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{now}] 状态检查:")
                
                # 流量信息
                traffic = self.get_traffic_info()
                if traffic:
                    up = traffic.get('up', 0)
                    down = traffic.get('down', 0)
                    print(f"  流量: ↑{self.format_bytes(up)} ↓{self.format_bytes(down)}")
                
                # 连接信息
                connections = self.get_connections()
                if connections:
                    conn_count = len(connections.get('connections', []))
                    print(f"  连接数: {conn_count}")
                    
                    # 统计用户连接
                    user_stats = {}
                    for conn in connections.get('connections', []):
                        metadata = conn.get('metadata', {})
                        user = metadata.get('inboundUser', 'unknown')
                        if user not in user_stats:
                            user_stats[user] = 0
                        user_stats[user] += 1
                    
                    if user_stats:
                        print("  用户连接统计:")
                        for user, count in user_stats.items():
                            print(f"    {user}: {count}")
                
                # 代理状态
                proxies = self.get_proxies()
                if proxies:
                    proxy_groups = proxies.get('proxies', {})
                    print(f"  代理组数量: {len(proxy_groups)}")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n监控已停止")
                break
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(interval)
    
    def format_bytes(self, bytes_val):
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f}TB"

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Mihomo服务监控')
    parser.add_argument('--api', default='http://127.0.0.1:9093', help='API地址')
    parser.add_argument('--secret', help='API密钥')
    parser.add_argument('--interval', type=int, default=30, help='监控间隔(秒)')
    
    args = parser.parse_args()
    
    monitor = MihomoMonitor(args.api, args.secret)
    monitor.monitor_loop(args.interval)
```

## 使用示例

### 1. 配置管理

```bash
# 添加VIP用户
python config_manager.py add-user "vip001/vip002" VIP_US

# 添加普通用户
python config_manager.py add-user "user001/user002" STANDARD_HK

# 列出所有用户规则
python config_manager.py list-users

# 删除用户规则
python config_manager.py remove-user "vip001/vip002"
```

### 2. 客户端使用

```bash
# VIP用户使用美国线路
curl --proxy-user vip001:password --proxy http://proxy.example.com:7891 http://httpbin.org/ip

# 普通用户使用香港线路
curl --proxy-user user001:password --proxy http://proxy.example.com:7891 http://httpbin.org/ip
```

### 3. 监控服务

```bash
# 启动监控
python monitor.py --api http://127.0.0.1:9093 --secret your-secret --interval 30
```

## 故障排除

### 1. 常见问题

**问题**: 规则不生效
**解决**: 
- 检查规则顺序，确保 PROXY-USER 规则在前面
- 检查用户名是否正确
- 查看日志确认用户认证成功

**问题**: 编译失败
**解决**:
- 确保 Go 版本 >= 1.19
- 检查依赖是否完整: `go mod tidy`
- 清理缓存: `go clean -cache`

**问题**: 连接失败
**解决**:
- 检查代理服务器配置
- 验证网络连通性
- 查看防火墙设置

### 2. 调试模式

启用详细日志：
```yaml
log-level: debug
```

查看匹配过程：
```
[DEBUG] ProxyUser.Match called: InUser=feifeimao, ExpectedUsers=[feifeimao]
[DEBUG] ProxyUser.Match: MATCHED! User feifeimao using adapter VIP_PROXY
```

## 性能优化

1. **规则优化**: 将常用规则放在前面
2. **连接池**: 配置合适的连接池大小
3. **DNS缓存**: 启用DNS缓存减少查询延迟
4. **负载均衡**: 使用多个代理服务器分担负载

## 安全建议

1. **API安全**: 设置强密码保护管理API
2. **用户认证**: 使用复杂密码
3. **网络隔离**: 限制管理端口访问
4. **日志审计**: 定期检查访问日志
5. **更新维护**: 及时更新到最新版本