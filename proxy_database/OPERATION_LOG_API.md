# 操作日志API文档

## 概述

操作日志功能用于记录账号相关的操作行为，提供完整的操作审计跟踪。

## 数据库表结构

### operation_log 表

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INT | 主键ID | PRIMARY KEY, AUTO_INCREMENT |
| account_id | INT | 关联账号ID | NOT NULL, INDEX |
| date_time | DATETIME | 操作时间 | NOT NULL |
| operation_json | JSON | 操作详情 | NOT NULL |
| createtime | DATETIME | 记录创建时间 | DEFAULT CURRENT_TIMESTAMP |

## API接口

### 创建操作日志

**接口地址:** `POST /operation-logs/`

**请求参数:**

```json
{
    "account_id": 1,
    "datetime": "2025-01-15T10:30:00",
    "operation_json": {
        "action": "login",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "result": "success",
        "details": {
            "login_method": "password",
            "session_id": "abc123def456"
        }
    }
}
```

**参数说明:**

- `account_id` (int, 必填): 关联的账号记录ID，必须是account_records表中存在的ID
- `datetime` (string, 必填): 操作发生的时间，ISO格式
- `operation_json` (object, 必填): 操作详情的JSON对象，可以包含任意结构的数据

**响应示例:**

```json
{
    "id": 1,
    "account_id": 1,
    "date_time": "2025-01-15T10:30:00",
    "operation_json": {
        "action": "login",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "result": "success",
        "details": {
            "login_method": "password",
            "session_id": "abc123def456"
        }
    },
    "createtime": "2025-01-15T10:30:05"
}
```

**错误响应:**

- `404 Not Found`: 当account_id对应的账号记录不存在时
- `422 Unprocessable Entity`: 当请求参数格式错误时

## 使用示例

### Python 示例

```python
import requests
from datetime import datetime

# 创建操作日志
data = {
    "account_id": 1,
    "datetime": datetime.now().isoformat(),
    "operation_json": {
        "action": "password_change",
        "ip_address": "192.168.1.100",
        "old_password_hash": "hash1",
        "new_password_hash": "hash2",
        "result": "success"
    }
}

response = requests.post(
    "http://localhost:8202/operation-logs/",
    json=data
)

if response.status_code == 200:
    print("操作日志创建成功:", response.json())
else:
    print("创建失败:", response.text)
```

### curl 示例

```bash
curl -X POST "http://localhost:8202/operation-logs/" \
     -H "Content-Type: application/json" \
     -d '{
       "account_id": 1,
       "datetime": "2025-01-15T10:30:00",
       "operation_json": {
         "action": "login",
         "ip_address": "192.168.1.100",
         "result": "success"
       }
     }'
```

## 常见操作类型示例

### 1. 登录操作

```json
{
    "action": "login",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "result": "success",
    "login_method": "password"
}
```

### 2. 密码修改

```json
{
    "action": "password_change",
    "ip_address": "192.168.1.100",
    "result": "success",
    "changed_by": "user"
}
```

### 3. 账号状态变更

```json
{
    "action": "status_change",
    "old_status": "active",
    "new_status": "suspended",
    "reason": "security_violation",
    "operator": "admin"
}
```

### 4. 2FA设置

```json
{
    "action": "2fa_setup",
    "ip_address": "192.168.1.100",
    "result": "success",
    "method": "totp"
}
```

## 注意事项

1. **数据验证**: account_id必须存在于account_records表中
2. **时间格式**: datetime字段使用ISO 8601格式
3. **JSON灵活性**: operation_json字段可以存储任意结构的JSON数据
4. **索引优化**: account_id字段已建立索引，便于快速查询
5. **审计跟踪**: 所有记录都有createtime字段记录插入时间

## 数据库迁移

系统启动时会自动检查并创建operation_log表，无需手动执行迁移脚本。如果表已存在，不会重复创建。