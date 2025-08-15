# Clash-Meta 压力测试

## 测试目标
使用 `locust` 框架完成压力测试，测试 clash-meta 在多连接下的性能表现以及瓶颈。

## 测试特点
- clash-meta 只做流量转发和维持，所以和常规 RESTful API 测试不一样
- 二次开发的 clash-meta 支持通过 UserProxy 进行代理认证
- 代理格式: `curl -x "http://192.168.132.58:7891" --proxy-user "71qppq:Z9sDUSVAtVmP" "https://www.google.com"`
- 测试URL不固定，每次从URL列表中随机选择
- 使用 locust 扩展完成系统性能监控，重点关注 CPU 和内存消耗

## 已完成的测试工具

### 1. 核心测试文件
- **locustfile.py**: 主要的 Locust 测试脚本，包含多种测试任务
- **comprehensive_stress_test.py**: 综合测试脚本，支持多场景和详细监控
- **config.py**: 配置文件，包含代理设置、用户凭据、测试场景等

### 2. 测试场景
- **轻量测试**: 10用户, 2/秒启动, 5分钟
- **中等测试**: 50用户, 5/秒启动, 10分钟  
- **重度测试**: 100用户, 10/秒启动, 15分钟
- **极限测试**: 200用户, 20/秒启动, 20分钟

### 3. 监控功能
- 实时系统资源监控 (CPU、内存、网络)
- Clash-Meta 进程专项监控
- 连接数统计
- 性能图表生成

### 4. 使用方法

#### 快速启动 (推荐)
```bash
# Windows
run_test.bat

# 选择测试场景后自动运行
```

#### 命令行运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行预设场景
python comprehensive_stress_test.py --scenario light

# 自定义测试
python comprehensive_stress_test.py --users 100 --spawn-rate 10 --duration 15m

# Web界面模式
locust -f locustfile.py --host=http://localhost --web-host=0.0.0.0
```

### 5. 测试输出
- HTML 详细报告
- CSV 统计数据
- JSON 监控数据
- 性能图表 (CPU/内存使用率)
- 综合分析报告

### 6. 代理认证格式
测试脚本使用从 `aggregated_clash_config_credentials.txt` 提取的真实用户凭据:
```
用户名: dp1_n6p5iypo, 密码: lIdIpNDSLKfWBaPp
用户名: dp1_j6xaudjt, 密码: MdmQRf7aHtvMZBsv
用户名: dp1_v9abt0zb, 密码: RDh0J8UMjA7ti1fu
用户名: dp1_v66t8aol, 密码: Z0EWTKPQqlxXQiHi
```

### 7. 测试URL列表
随机从以下URL中选择测试目标:
- https://www.google.com
- https://httpbin.org/get
- https://httpbin.org/ip
- https://www.github.com
- https://api.github.com
- https://jsonplaceholder.typicode.com/posts/1
- 等等...

## 开始测试
1. 确保 Clash-Meta 服务运行在 `192.168.132.58:7891`
2. 运行 `run_test.bat` 选择测试场景
3. 查看生成的报告和图表分析性能瓶颈