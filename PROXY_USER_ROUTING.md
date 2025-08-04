# Clash-Meta 代理用户路由扩展

## 功能概述

这个扩展为 clash-meta 添加了基于代理认证用户名的路由功能。通过 `PROXY-USER` 规则类型，可以根据不同的代理认证用户名将流量路由到不同的代理服务器。

## 实现原理

1. **用户认证**: 当客户端使用 `--proxy-user username:password` 连接代理时，clash-meta 会提取用户名
2. **规则匹配**: 新增的 `PROXY-USER` 规则会检查 `metadata.InUser` 字段
3. **流量路由**: 匹配成功后，将流量路由到指定的代理组

## 配置语法

```yaml
rules:
  - 'PROXY-USER,username,PROXY_GROUP'
  - 'PROXY-USER,user1/user2/user3,PROXY_GROUP'  # 支持多用户
```

## 配置示例

```yaml
mixed-port: 7891
allow-lan: true
external-controller: 0.0.0.0:9093
bind-address: '*'
mode: rule
log-level: debug

proxies:
  - { name: 'US-01', type: ss, server: example.com, port: '20001', cipher: aes-256-gcm, password: your-password, udp: true }
  - { name: 'HK-01', type: ss, server: example.com, port: '16001', cipher: aes-256-gcm, password: your-password, udp: true }

proxy-groups:
  - { name: 'VIP_PROXY', type: select, proxies: ['US-01'] }
  - { name: 'NORMAL_PROXY', type: select, proxies: ['HK-01'] }

rules:
  # VIP用户走美国代理
  - 'PROXY-USER,feifeimao,VIP_PROXY'
  - 'PROXY-USER,vipuser/premium,VIP_PROXY'
  
  # 测试域名
  - 'DOMAIN-SUFFIX,httpbin.org,NORMAL_PROXY'
  
  # 本地直连
  - 'IP-CIDR,127.0.0.0/8,DIRECT'
  - 'IP-CIDR,192.168.0.0/16,DIRECT'
  - 'IP-CIDR,10.0.0.0/8,DIRECT'
  
  # 默认规则 - 其他用户走香港代理
  - 'MATCH,NORMAL_PROXY'
```

## 使用方法

### 1. curl 命令
```bash
# VIP用户 feifeimao 走美国代理
curl --proxy-user feifeimao:7212 --proxy http://127.0.0.1:7891 http://httpbin.org/ip

# 普通用户走香港代理
curl --proxy-user normaluser:7212 --proxy http://127.0.0.1:7891 http://httpbin.org/ip
```

### 2. Python requests
```python
import requests

# VIP用户配置
vip_proxies = {
    'http': 'http://feifeimao:7212@127.0.0.1:7891',
    'https': 'http://feifeimao:7212@127.0.0.1:7891'
}

# 普通用户配置
normal_proxies = {
    'http': 'http://normaluser:7212@127.0.0.1:7891', 
    'https': 'http://normaluser:7212@127.0.0.1:7891'
}

# 发送请求
response = requests.get('http://httpbin.org/ip', proxies=vip_proxies)
```

### 3. 浏览器配置
在浏览器代理设置中：
- 代理服务器: 127.0.0.1:7891
- 用户名: feifeimao (VIP用户) 或 normaluser (普通用户)
- 密码: 7212

## 构建和测试

### 1. 构建项目
```bash
go build -o mihomo-custom.exe .
```

### 2. 运行测试
```bash
# Windows
build_and_test.bat

# 或手动运行
mihomo-custom.exe -f proxy_user_config.yaml
```

### 3. 测试脚本
```bash
python test_proxy_user.py
```

## 代码修改说明

### 1. 添加新规则类型 (constant/rule.go)
```go
const (
    // ... 其他规则类型
    HTTPHeader
    ProxyUser  // 新增
)

func (rt RuleType) String() string {
    // ... 其他case
    case ProxyUser:
        return "ProxyUser"
}
```

### 2. 实现规则逻辑 (rules/common/proxy_user.go)
```go
type ProxyUser struct {
    *Base
    users   []string
    adapter string
    payload string
}

func (p *ProxyUser) Match(metadata *C.Metadata, helper C.RuleMatchHelper) (bool, string) {
    for _, user := range p.users {
        if metadata.InUser == user {
            return true, p.adapter
        }
    }
    return false, ""
}
```

### 3. 注册规则解析器 (rules/parser.go)
```go
case "PROXY-USER":
    parsed, parseErr = RC.NewProxyUser(payload, target)
```

## 调试信息

启用 `log-level: debug` 后，可以看到详细的匹配日志：

```
[DEBUG] ProxyUser.Match called: InUser=feifeimao, ExpectedUsers=[feifeimao]
[DEBUG] ProxyUser.Match: MATCHED! User feifeimao using adapter VIP_PROXY
```

## 注意事项

1. **规则顺序**: `PROXY-USER` 规则应该放在配置文件的最前面，确保优先匹配
2. **用户认证**: 需要在 clash-meta 中配置相应的用户认证信息
3. **多用户支持**: 使用 `/` 分隔多个用户名，如 `user1/user2/user3`
4. **大小写敏感**: 用户名匹配是大小写敏感的
5. **调试模式**: 建议在测试时开启 `debug` 日志级别

## 应用场景

1. **多租户代理**: 为不同用户提供不同的代理线路
2. **VIP服务**: VIP用户使用高速线路，普通用户使用标准线路  
3. **地区分流**: 不同用户访问不同地区的服务器
4. **负载均衡**: 根据用户类型分配到不同的代理池

## 扩展可能

1. **用户组支持**: 支持用户组概念，简化配置
2. **动态配置**: 支持热重载用户路由规则
3. **统计功能**: 记录不同用户的流量使用情况
4. **限速功能**: 为不同用户设置不同的速度限制