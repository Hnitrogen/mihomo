# Curl 命令示例

## 1. 测试技术部门

```bash
curl -H "Authorization: Bearer your-api-secret" \
     "http://localhost:9093/department/secret?secret=dept001_secret_key"
```

## 2. 测试销售部门

```bash
curl -H "Authorization: Bearer your-api-secret" \
     "http://localhost:9093/department/secret?secret=dept002_secret_key"
```

## 3. 测试人事部门

```bash
curl -H "Authorization: Bearer your-api-secret" \
     "http://localhost:9093/department/secret?secret=dept003_secret_key"
```

## 4. 测试财务部门

```bash
curl -H "Authorization: Bearer your-api-secret" \
     "http://localhost:9093/department/secret?secret=dept004_secret_key"
```

## 5. 测试无效密钥（应该返回401）

```bash
curl -H "Authorization: Bearer your-api-secret" \
     "http://localhost:9093/department/secret?secret=invalid_secret"
```

## 6. 测试错误的API密钥（应该返回401）

```bash
curl -H "Authorization: Bearer wrong-api-secret" \
     "http://localhost:9093/department/secret?secret=dept001_secret_key"
```

## 7. 格式化输出（使用jq美化JSON）

```bash
curl -H "Authorization: Bearer your-api-secret" \
     "http://localhost:9093/department/secret?secret=dept001_secret_key" | jq
```

## 8. 显示详细信息（包括HTTP头）

```bash
curl -v -H "Authorization: Bearer your-api-secret" \
     "http://localhost:9093/department/secret?secret=dept001_secret_key"
```

## 9. 静默模式（只显示响应内容）

```bash
curl -s -H "Authorization: Bearer your-api-secret" \
     "http://localhost:9093/department/secret?secret=dept001_secret_key"
```

## Windows PowerShell 版本

如果在Windows PowerShell中使用，需要注意引号的处理：

```powershell
curl.exe -H "Authorization: Bearer your-api-secret" "http://localhost:9093/department/secret?secret=dept001_secret_key"
```

或者使用Invoke-WebRequest：

```powershell
$headers = @{ "Authorization" = "Bearer your-api-secret" }
Invoke-WebRequest -Uri "http://localhost:9093/department/secret?secret=dept001_secret_key" -Headers $headers
```