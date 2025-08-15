# 配置管理指南

## 概述

代理用户管理系统现在支持外部配置文件，你可以轻松修改 Clash Meta 的连接地址和其他系统设置，而无需修改代码。

## 配置文件

配置文件位于：`proxy_database/config.yaml`

### 主要配置项

#### 1. Clash Meta 配置
```yaml
clash_meta:
  api_url: "http://192.168.132.58:9093"  # Clash Meta API 地址
  config_endpoint: "/configs"             # API 端点
  auth_token: "seo-pinkman"              # 认证令牌
  timeout: 10                            # 请求超时时间（秒）
```

#### 2. 配置文件路径
```yaml
config_paths:
  clash_config_dir: "~/.config/mihomo"           # 配置文件保存目录
  clash_config_filename: "aggregated_clash_config.yaml"  # 配置文件名
```

#### 3. 数据库配置
```yaml
database:
  url: "sqlite:///./proxy_database.db"  # 数据库连接字符串
```

#### 4. 服务器配置
```yaml
server:
  host: "0.0.0.0"  # 服务监听地址
  port: 8202       # 服务监听端口
```

#### 5. 用户生成配置
```yaml
user_generation:
  username_length: 6   # 生成的用户名长度
  password_length: 12  # 生成的密码长度
```

#### 6. 部门配置
```yaml
departments:
  "1": "tech_dept"
  "2": "sales_dept"
  "3": "hr_dept"
  "4": "finance_dept"
```

## 使用方法

### 方法一：直接编辑配置文件
1. 编辑 `proxy_database/config.yaml` 文件
2. 修改需要的配置项
3. 重启服务使配置生效

### 方法二：使用Web界面
1. 访问系统主页
2. 点击 "⚙️ 系统配置管理" 按钮
3. 在配置管理页面修改设置
4. 点击 "💾 保存配置" 按钮
5. 重启服务使配置生效

## 常见配置场景

### 更改 Clash Meta 地址
如果你的 Clash Meta 运行在不同的服务器或端口上：

```yaml
clash_meta:
  api_url: "http://新的IP地址:新的端口"
  # 例如: "http://10.0.0.100:9093"
```

### 更改认证令牌
如果你修改了 Clash Meta 的认证令牌：

```yaml
clash_meta:
  auth_token: "你的新令牌"
```

### 更改服务端口
如果需要在不同端口运行此服务：

```yaml
server:
  port: 8080  # 新的端口号
```

## 注意事项

1. **重启服务**：修改配置后需要重启 Python 服务才能生效
2. **配置验证**：系统会在启动时验证配置文件，如果配置文件不存在或格式错误，会使用默认配置
3. **权限问题**：确保服务有权限访问配置的目录和文件
4. **网络连接**：确保配置的 Clash Meta API 地址可以正常访问

## 故障排除

### 配置文件不存在
如果 `config.yaml` 文件不存在，系统会自动使用默认配置并在控制台输出提示信息。

### 连接 Clash Meta 失败
检查以下项目：
1. Clash Meta 是否正在运行
2. API 地址和端口是否正确
3. 认证令牌是否正确
4. 网络连接是否正常

### 配置保存失败
确保：
1. 有写入 `config.yaml` 文件的权限
2. 磁盘空间充足
3. 配置格式正确