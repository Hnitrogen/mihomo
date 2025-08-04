# 部门密钥接口使用指南

## 概述

这个接口允许通过部门密钥获取该部门所有ProxyUser的账号、密码和订阅区域信息。

## 接口信息

- **接口地址**: `GET /department/secret`
- **参数**: `secret` (查询参数)
- **认证**: 需要在请求头中包含 `Authorization: Bearer <api_secret>`

## 配置要求

### 1. 在配置文件中添加部门密钥映射

```yaml
# 部门密钥映射配置
department-secrets:
  "dept001_secret_key": "tech_dept"      # 技术部门
  "dept002_secret_key": "sales_dept"     # 销售部门
  "dept003_secret_key": "hr_dept"        # 人事部门
  "dept004_secret_key": "finance_dept"   # 财务部门
```

### 2. 配置PROXY-USER规则

```yaml
rules:
  # 技术部门用户 - 走美国高速线路
  - 'PROXY-USER,tech_user1/tech_user2/tech_admin,VIP_US'
  
  # 销售部门用户 - 走香港线路
  - 'PROXY-USER,sales_user1/sales_user2/sales_manager,STANDARD_HK'
  
  # 人事部门用户 - 走日本线路
  - 'PROXY-USER,hr_user1/hr_user2,JAPAN_GROUP'
  
  # 财务部门用户 - 走香港线路
  - 'PROXY-USER,finance_user1/finance_user2,STANDARD_HK'
```

### 3. 启用外部控制器

```yaml
external-controller: 0.0.0.0:9093
secret: "your-api-secret"
```

## 使用示例

### 请求示例

```bash
curl -H "Authorization: Bearer your-api-secret" \
     "http://localhost:9093/department/secret?secret=dept001_secret_key"
```

### 响应示例

```json
{
  "department_id": "tech_dept",
  "users": [
    {
      "username": "tech_user1",
      "password": "TechPass123!",
      "region": "VIP专线"
    },
    {
      "username": "tech_user2", 
      "password": "TechPass456!",
      "region": "VIP专线"
    },
    {
      "username": "tech_admin",
      "password": "AdminTech789!",
      "region": "VIP专线"
    }
  ]
}
```

## 错误响应

### 缺少密钥参数
```json
{
  "message": "Missing secret parameter"
}
```
状态码: 400

### 无效密钥
```json
{
  "message": "Invalid secret"
}
```
状态码: 401

### 未授权访问
```json
{
  "message": "Unauthorized"
}
```
状态码: 401

## 用户-部门映射逻辑

系统使用以下逻辑来判断用户是否属于指定部门：

1. **用户名包含部门ID**: 如果用户名包含部门ID，则认为属于该部门
2. **前缀匹配**:
   - 技术部门: `tech_`, `dev_`, `engineer_` 开头的用户名
   - 销售部门: `sales_`, `sale_` 开头的用户名  
   - 人事部门: `hr_`, `human_` 开头的用户名
   - 财务部门: `finance_`, `accounting_` 开头的用户名

## 地区推断逻辑

系统根据代理组名称推断用户的订阅地区：

- 包含 `US` 或 `AMERICA` → "美国"
- 包含 `HK` 或 `HONGKONG` → "香港"  
- 包含 `JP` 或 `JAPAN` → "日本"
- 包含 `SG` 或 `SINGAPORE` → "新加坡"
- 包含 `VIP` → "VIP专线"
- 其他 → "未知地区"

## 密码管理

当前实现包含一个示例密码映射。在生产环境中，建议：

1. 从安全的数据库或配置文件中读取密码
2. 使用加密存储密码
3. 实现密码轮换机制
4. 记录密码访问日志

## 测试

使用提供的测试脚本验证接口功能：

```bash
python test_department_api.py
```

## 安全注意事项

1. **API密钥保护**: 确保API密钥安全存储，不要在代码中硬编码
2. **HTTPS**: 在生产环境中使用HTTPS加密传输
3. **访问控制**: 限制接口访问来源IP
4. **日志记录**: 记录所有接口访问日志用于审计
5. **密钥轮换**: 定期更换部门密钥和API密钥

## 扩展功能

可以考虑添加以下功能：

1. **用户状态管理**: 添加用户启用/禁用状态
2. **使用统计**: 记录用户使用情况和流量统计
3. **批量操作**: 支持批量获取多个部门信息
4. **缓存机制**: 添加响应缓存提高性能
5. **Webhook通知**: 当用户信息变更时发送通知