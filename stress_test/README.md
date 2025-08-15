# Clash-Meta 压力测试

基于 Locust 框架的 Clash-Meta 代理性能压力测试工具，专门测试 clash-meta 在多连接下的性能表现和瓶颈。

## 功能特点

- 🚀 **多用户并发测试**: 模拟多个用户同时通过代理访问不同网站
- 📊 **实时系统监控**: 监控 CPU、内存、网络等系统资源使用情况
- 📈 **详细性能报告**: 生成 HTML 报告和性能图表
- 🎯 **多种测试场景**: 轻量、中等、重度、极限四种预设场景
- 🔧 **灵活配置**: 支持自定义测试参数
- 📋 **综合分析**: 提供测试结果的深度分析

## 文件结构

```
stress_test/
├── locustfile.py              # 主要的 Locust 测试文件
├── comprehensive_stress_test.py # 综合测试脚本
├── config.py                  # 配置文件
├── requirements.txt           # Python 依赖
├── run_test.bat              # Windows 启动脚本
└── README.md                 # 说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包：
- `locust`: 压力测试框架
- `psutil`: 系统监控
- `matplotlib`: 图表生成
- `pandas`: 数据处理
- `requests`: HTTP 请求

## 使用方法

### 步骤0：验证用户凭据 (必须)

在运行压力测试前，需要先验证user.csv中的用户凭据：

```bash
# 方法1: 使用批处理脚本 (推荐)
validate_users.bat

# 方法2: 直接运行Python脚本
python validate_users.py

# 方法3: 快速测试前10个用户
python quick_test.py
```

验证完成后会生成 `valid_users_config.py` 文件，包含所有有效的用户凭据。

### 方法一：使用启动脚本 (推荐)

双击运行 `run_test.bat`，选择测试场景：

1. **轻量测试**: 10用户, 5分钟
2. **中等测试**: 50用户, 10分钟  
3. **重度测试**: 100用户, 15分钟
4. **极限测试**: 200用户, 20分钟
5. **自定义测试**: 自定义参数
6. **Web界面模式**: 通过浏览器控制
7. **运行所有场景**: 依次运行所有预设场景

### 方法二：命令行运行

```bash
# 运行预设场景
python comprehensive_stress_test.py --scenario light

# 自定义参数
python comprehensive_stress_test.py --users 100 --spawn-rate 10 --duration 15m

# 运行所有场景
python comprehensive_stress_test.py --all-scenarios

# 不生成图表 (节省时间)
python comprehensive_stress_test.py --scenario medium --no-charts
```

### 方法三：Web界面模式

```bash
locust -f locustfile.py --host=http://localhost --web-host=0.0.0.0
```

然后在浏览器中访问 `http://localhost:8089`

## 测试配置

### 代理配置 (config.py)

```python
PROXY_CONFIG = {
    'host': '192.168.132.58',  # Clash-Meta 服务器地址
    'port': 7891,              # 代理端口
    'timeout': 30              # 请求超时时间
}
```

### 测试用户凭据

测试脚本会使用从 `user.csv` 验证后的有效用户凭据：

1. **user.csv格式**:
   ```
   username,password
   fgamz7,zKBRKcOKzbU0
   ef2tqz,b4J4td38hknU
   ...
   ```

2. **验证过程**:
   - 读取user.csv中的所有用户
   - 并发测试每个用户的代理连接
   - 生成有效用户配置文件

3. **生成的配置**:
   ```python
   PROXY_USERS = [
       {"username": "fgamz7", "password": "zKBRKcOKzbU0"},
       {"username": "ef2tqz", "password": "b4J4td38hknU"},
       # ... 更多验证通过的用户
   ]
   ```

### 测试目标URL

脚本会随机从以下URL列表中选择目标进行测试：

- Google、GitHub 等常用网站
- HTTPBin API 测试接口
- JSON API 测试
- 延迟测试接口

## 测试场景说明

| 场景 | 用户数 | 启动速率 | 持续时间 | 适用场景 |
|------|--------|----------|----------|----------|
| light | 10 | 2/秒 | 5分钟 | 基础功能验证 |
| medium | 50 | 5/秒 | 10分钟 | 日常负载测试 |
| heavy | 100 | 10/秒 | 15分钟 | 高负载测试 |
| extreme | 200 | 20/秒 | 20分钟 | 极限性能测试 |

## 监控指标

### 系统监控
- CPU 使用率
- 内存使用率和可用内存
- 磁盘使用率
- 网络 I/O 统计

### Clash-Meta 进程监控
- 进程 CPU 使用率
- 进程内存使用量
- 活跃连接数
- 进程状态

### 请求性能指标
- 总请求数
- 失败请求数
- 平均响应时间
- 最大响应时间
- 每秒请求数 (RPS)
- 失败率

## 输出文件

测试完成后会生成以下文件：

### 报告文件
- `report_[场景名].html`: Locust 生成的详细 HTML 报告
- `comprehensive_report_[场景名]_[时间戳].json`: 综合测试报告

### 数据文件
- `results_[场景名]_stats.csv`: 详细的统计数据
- `monitoring_stats_[场景名]_[时间戳].json`: 系统监控数据

### 图表文件 (在 [场景名]_charts 目录中)
- `cpu_usage.png`: CPU 使用率图表
- `memory_usage.png`: 内存使用率图表
- `system_resources.png`: 综合资源使用图表

## 注意事项

1. **网络环境**: 确保测试机器能够访问目标URL
2. **代理配置**: 确认 Clash-Meta 服务正在运行且配置正确
3. **用户凭据**: 确保测试用户凭据有效且未过期
4. **系统资源**: 极限测试可能消耗大量系统资源
5. **防火墙**: 确保防火墙不会阻止测试连接

## 故障排除

### 常见问题

1. **连接被拒绝**
   - 检查 Clash-Meta 是否正在运行
   - 确认代理地址和端口配置正确

2. **认证失败**
   - 检查用户名和密码是否正确
   - 确认用户凭据未过期

3. **依赖安装失败**
   - 使用 `pip install --upgrade pip` 更新 pip
   - 尝试使用 `pip install -r requirements.txt --user`

4. **图表生成失败**
   - 安装额外的图形库: `pip install pillow`
   - 使用 `--no-charts` 参数跳过图表生成

## 性能优化建议

根据测试结果，可以考虑以下优化：

1. **连接池优化**: 调整 Clash-Meta 的连接池大小
2. **内存管理**: 监控内存使用，避免内存泄漏
3. **网络配置**: 优化网络缓冲区和超时设置
4. **负载均衡**: 在多个代理节点间分配负载

## 扩展功能

可以根据需要添加以下功能：

1. **更多协议支持**: SOCKS5、HTTP/2 等
2. **地理位置测试**: 测试不同地区的代理性能
3. **长连接测试**: WebSocket 等长连接协议
4. **文件传输测试**: 大文件上传下载性能

---

**祝你的 Clash-Meta 压力测试顺利！** 🚀