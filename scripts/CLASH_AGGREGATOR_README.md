# Clash 配置文件聚合器

这是一个Python脚本，用于聚合多个Clash订阅配置文件，并为每个代理节点生成随机的用户认证规则。

## 功能特性

- ✅ 聚合多个Clash配置文件的proxies
- ✅ 为每个代理节点生成随机用户名和密码
- ✅ 保留原有的PROXY-USER规则
- ✅ 自动创建VIP_PROXY和NORMAL_PROXY代理组
- ✅ 生成标准的路由规则
- ✅ 输出用户凭据信息文件

## 安装依赖

```bash
pip install PyYAML
```

## 使用方法

### 方法1: 使用示例脚本（推荐）

```bash
python example_usage.py
```

这会自动聚合当前目录下的 `nicai.yaml` 和 `nicai_simple.yaml` 文件。

### 方法2: 命令行方式

```bash
# 聚合指定的配置文件
python clash_aggregator.py config1.yaml config2.yaml config3.yaml

# 指定输出文件名
python clash_aggregator.py config1.yaml config2.yaml -o my_config.yaml
```

### 方法3: 使用批处理文件（Windows）

双击运行 `run_aggregator.bat`

## 输出文件

运行后会生成两个文件：

1. **aggregated_clash_config.yaml** - 聚合后的Clash配置文件
2. **aggregated_clash_config_credentials.txt** - 生成的用户凭据信息

## 生成的规则结构

```yaml
rules:
  # 现有的代理用户认证规则（如果有）
  - 'PROXY-USER,feifeimao,VIP_PROXY'
  - 'PROXY-USER,vipuser,VIP_PROXY'
  - 'PROXY-USER,normaluser,NORMAL_PROXY'
  - 'PROXY-USER,autouser,VIP_PROXY'
  
  # 新生成的代理用户认证规则
  - 'PROXY-USER,u2weix0q,VIP_PROXY'
  - 'PROXY-USER,hi5nqsxx,NORMAL_PROXY'
  # ... 更多随机生成的用户规则
  
  # 测试域名
  - 'DOMAIN-SUFFIX,httpbin.org,NORMAL_PROXY'
  - 'DOMAIN-SUFFIX,google.com,NORMAL_PROXY'
  
  # 本地直连
  - 'IP-CIDR,127.0.0.0/8,DIRECT'
  - 'IP-CIDR,192.168.0.0/16,DIRECT'
  - 'IP-CIDR,10.0.0.0/8,DIRECT'
  
  # 默认规则
  - 'MATCH,NORMAL_PROXY'
```

## 代理组配置

脚本会自动创建以下代理组：

- **VIP_PROXY**: VIP用户专用代理组
- **NORMAL_PROXY**: 普通用户代理组
- **AUTO**: 自动选择最快节点（如果有多个代理）

## 用户认证

每个代理节点都会生成一个对应的用户认证规则：

- 用户名：8位随机字符（小写字母+数字）
- 密码：8位随机字符（大小写字母+数字）
- 代理组：随机分配到VIP_PROXY或NORMAL_PROXY

## 配置文件结构

生成的配置文件包含：

```yaml
mixed-port: 7891
allow-lan: true
external-controller: 0.0.0.0:9093
mode: rule
log-level: info

# 用户认证列表
authentication:
  - "username1:password1"
  - "username2:password2"
  # ...

# 聚合的代理列表
proxies:
  - name: "代理1"
    type: ss
    server: "..."
    # ...

# 代理组
proxy-groups:
  - name: VIP_PROXY
    type: select
    proxies: [...]
  - name: NORMAL_PROXY
    type: select
    proxies: [...]

# 路由规则
rules:
  # PROXY-USER规则
  # 测试域名规则
  # 本地直连规则
  # 默认规则
```

## 注意事项

1. 脚本会保留原配置文件中已存在的PROXY-USER规则
2. 新生成的用户名不会与现有用户名重复
3. 代理会随机分配到VIP_PROXY和NORMAL_PROXY组
4. 生成的凭据信息保存在单独的txt文件中，请妥善保管

## 示例输出

```
找到以下配置文件:
  - nicai.yaml
  - nicai_simple.yaml

开始聚合...
处理文件: nicai.yaml
  - 提取到 37 个代理
  - 提取到 0 个PROXY-USER规则
处理文件: nicai_simple.yaml
  - 提取到 2 个代理
  - 提取到 4 个PROXY-USER规则

总计聚合了 39 个代理

聚合配置已保存到: aggregated_clash_config.yaml
用户凭据信息已保存到: aggregated_clash_config_credentials.txt

聚合完成!
- 输出文件: aggregated_clash_config.yaml
- 总代理数量: 39
- 生成用户数量: 39
- 保留现有规则: 4
```

## 故障排除

1. **ImportError: No module named 'yaml'**
   ```bash
   pip install PyYAML
   ```

2. **文件不存在错误**
   - 确保配置文件路径正确
   - 检查文件名拼写

3. **YAML格式错误**
   - 确保输入的配置文件是有效的YAML格式
   - 检查文件编码是否为UTF-8