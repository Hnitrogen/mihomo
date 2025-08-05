# 代理用户管理系统

使用FastAPI构建的轻量级web服务，用于维护ProxyUser账号信息与订阅节点的关系。

## 功能特性

- 📁 **YAML文件上传**: 支持上传clash配置文件，自动解析proxies节点
- 🔐 **自动生成账号**: 为每个代理节点自动生成唯一的用户名(6位)和密码(12位)
- 🏢 **部门管理**: 支持按部门ID分类管理代理节点
- 📊 **数据管理界面**: 提供分页查看、筛选、删除等功能
- 💾 **SQLite数据库**: 使用轻量级SQLite数据库存储数据

## 数据库表结构

```sql
CREATE TABLE proxy (
    id INTEGER PRIMARY KEY,
    proxy_name VARCHAR,      -- 节点名称
    proxy TEXT,             -- 机场config行(完整配置)
    source_type VARCHAR,    -- 机场名称
    username VARCHAR UNIQUE, -- userProxy账号(6位)
    password VARCHAR,       -- userProxy密码(12位)
    department_id VARCHAR,  -- 部门ID
    updatetime DATETIME,    -- 更新时间
    createtime DATETIME     -- 创建时间
);
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python proxy-sync.py
```

或者在Windows上运行:
```bash
start_server.bat
```

### 3. 访问界面

- 主页(上传文件): http://localhost:8000
- 数据管理界面: http://localhost:8000/ui

## API接口

### 上传YAML文件
```
POST /upload-yaml/
Content-Type: multipart/form-data

参数:
- file: YAML文件
- source_type: 机场名称
- department_id: 部门ID
```

### 获取代理列表
```
GET /proxies/?page=1&size=10&source_type=xxai&department_id=1
```

### 获取代理总数
```
GET /proxies/count?source_type=xxai&department_id=1
```

### 删除代理
```
DELETE /proxies/{proxy_id}
```

## 使用示例

1. **上传YAML文件**:
   - 访问 http://localhost:8000
   - 选择clash配置的YAML文件
   - 填写机场名称(如: xxai, userdog)
   - 选择部门ID(1-4)
   - 点击上传

2. **查看生成的账号**:
   - 上传成功后会显示为每个代理节点生成的用户名和密码
   - 用户名格式: 6位随机字符(小写字母+数字)
   - 密码格式: 12位随机字符(大小写字母+数字)

3. **管理代理数据**:
   - 访问 http://localhost:8000/ui
   - 可以按机场名称、部门ID筛选
   - 支持分页浏览
   - 可以删除不需要的代理

## 部门ID说明

- 1: 技术部门
- 2: 销售部门  
- 3: 人事部门
- 4: 财务部门

## 注意事项

- 用户名保证全局唯一，如果生成重复会自动重新生成
- 数据库文件 `proxy_database.db` 会自动创建在当前目录
- 支持的文件格式: `.yaml`, `.yml`
- 服务默认运行在 `http://localhost:8000`

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite
- **前端**: HTML + CSS + JavaScript
- **模板引擎**: Jinja2
- **YAML解析**: PyYAML