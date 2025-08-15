#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用FastAPI编写轻量级web应用
维护ProxyUser账号信息与订阅节点的关系
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import JSON, create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import yaml
import random
import string
import os
from typing import List, Optional
from pydantic import BaseModel

# 加载配置文件
def load_config():
    """加载配置文件"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.yaml")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"配置文件 {config_path} 不存在，使用默认配置")
        return {
            "clash_meta": {
                "api_url": "http://192.168.132.58:9093",
                "config_endpoint": "/configs",
                "auth_token": "seo-pinkman",
                "timeout": 10
            },
            "config_paths": {
                "clash_config_dir": "~/.config/mihomo",
                "clash_config_filename": "aggregated_clash_config.yaml"
            },
            "database": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "username": "root",
                "password": "7212",
                "database": "ugc",
                "charset": "utf8mb4",
                "url": "mysql+pymysql://root:7212@localhost:3306/ugc?charset=utf8mb4"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8202
            },
            "user_generation": {
                "username_length": 6,
                "password_length": 12
            },
            "departments": {
                "1": "tech_dept",
                "2": "sales_dept",
                "3": "hr_dept",
                "4": "finance_dept"
            }
        }

# 加载配置
config = load_config()

# 数据库配置
SQLALCHEMY_DATABASE_URL = config["database"]["url"]
# MySQL不需要check_same_thread参数，这是SQLite特有的
if "mysql" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库模型
class ProxyModel(Base):
    __tablename__ = "proxy"
    
    id = Column(Integer, primary_key=True, index=True)
    proxy_name = Column(String(255), index=True)  # 节点名称
    proxy = Column(Text)  # 机场config行
    source_type = Column(String(100))  # 机场名
    username = Column(String(100), unique=True, index=True)  # userProxy账号
    password = Column(String(255))  # userProxy密码
    department_id = Column(String(50))  # 部门id
    before_update = Column(Text)  # 更新前的proxy配置
    ip = Column(String(45))  # proxy的真实IP (IPv6最长39字符，留点余量)
    before_ip = Column(String(45))  # 冗余记录IP
    country = Column(String(100))  # 国家
    status = Column(String(50))  # IP是否可用状态
    ip_check_data = Column(JSON)  # 记录IP检查数据
    updatetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    createtime = Column(DateTime, default=datetime.now)

class AccountRecordsModel(Base):
    __tablename__ = "account_records"
    
    id = Column(Integer, primary_key=True, index=True)
    proxy_id = Column(Integer, index=True)    # 逻辑外键
    account = Column(String(255), nullable=False)  # 账号（非空）
    account_password = Column(String(255), nullable=False)  # 账号密码（非空）
    auxiliary_email = Column(String(255))  # 辅助邮箱
    two_fa = Column(String(255))  # 2FA
    hubstudio_container_id = Column(String(255))  # hubstudio容器id
    createtime = Column(DateTime, default=datetime.now)  # 创建时间
    updatetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间（触发器自动更新）
    init_account_time = Column(DateTime)  # 初始化账号时间
    status = Column(String(20), default="active")  # 状态，账号是否被封禁
    account_type = Column(String(20))  # 账号类型
    user_name = Column(String(20))  # 使用人

class ChangeLogModel(Base):
    __tablename__ = "change_log"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer)     # 原表中的Id
    table_name = Column(String(100), nullable=False)  # 表名
    field = Column(String(100), nullable=False)  # 字段名
    before_change = Column(Text)  # 记录变更前的信息
    createtime = Column(DateTime, default=datetime.now)  # 创建时间

class OperationLogModel(Base):
    __tablename__ = "operation_log"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False, index=True)  # 关联AccountRecordsModel的id
    date_time = Column(DateTime, nullable=False)  # 日志时间
    operation_json = Column(JSON, nullable=False)  # 操作日志 JSON格式
    createtime = Column(DateTime, default=datetime.now)  # 创建时间

# 数据库迁移函数
def migrate_database():
    """检查并添加新字段"""
    db = SessionLocal()
    from sqlalchemy import text
    
    # proxy表需要添加的字段列表
    proxy_new_fields = [
        ("before_update", "TEXT"),
        ("ip", "VARCHAR(45)"),
        ("before_ip", "VARCHAR(45)"),
        ("country", "VARCHAR(100)"),
        ("status", "VARCHAR(50)")
    ]
    
    # account_records表需要添加的字段列表
    account_records_new_fields = [
        ("proxy_id", "INT"),
        ("status", "VARCHAR(20) DEFAULT 'active'"),
        ("account_type", "VARCHAR(20)"),
        ("user_name", "VARCHAR(20)")
    ]
    
    # 迁移proxy表字段
    for field_name, field_type in proxy_new_fields:
        try:
            # 尝试查询字段，如果不存在会抛出异常
            db.execute(text(f"SELECT {field_name} FROM proxy LIMIT 1"))
            print(f"proxy表字段 {field_name} 已存在")
        except Exception:
            # 字段不存在，添加字段
            try:
                db.execute(text(f"ALTER TABLE proxy ADD COLUMN {field_name} {field_type}"))
                db.commit()
                print(f"成功添加proxy表字段 {field_name}")
            except Exception as e:
                print(f"添加proxy表字段 {field_name} 失败: {e}")
    
    # 迁移account_records表字段
    for field_name, field_type in account_records_new_fields:
        try:
            # 尝试查询字段，如果不存在会抛出异常
            db.execute(text(f"SELECT {field_name} FROM account_records LIMIT 1"))
            print(f"account_records表字段 {field_name} 已存在")
        except Exception:
            # 字段不存在，添加字段
            try:
                db.execute(text(f"ALTER TABLE account_records ADD COLUMN {field_name} {field_type}"))
                db.commit()
                print(f"成功添加account_records表字段 {field_name}")
            except Exception as e:
                print(f"添加account_records表字段 {field_name} 失败: {e}")
    
    # 检查并创建operation_log表
    try:
        db.execute(text("SELECT 1 FROM operation_log LIMIT 1"))
        print("operation_log表已存在")
    except Exception:
        # 表不存在，创建表
        try:
            create_operation_log_sql = """
            CREATE TABLE operation_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                account_id INT NOT NULL,
                date_time DATETIME NOT NULL,
                operation_json JSON NOT NULL,
                createtime DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_account_id (account_id)
            )
            """
            db.execute(text(create_operation_log_sql))
            db.commit()
            print("成功创建operation_log表")
        except Exception as e:
            print(f"创建operation_log表失败: {e}")
    
    db.close()

# 创建数据库表
Base.metadata.create_all(bind=engine)
# 执行数据库迁移
migrate_database()

# Pydantic模型
class ProxyResponse(BaseModel):
    id: int
    proxy_name: str
    proxy: str
    source_type: str
    username: str
    password: str
    department_id: str
    before_update: Optional[str] = None
    ip: Optional[str] = None
    before_ip: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None
    updatetime: datetime
    createtime: datetime
    
    class Config:
        from_attributes = True

class ProxyCreate(BaseModel):
    source_type: str
    department_id: str

class AccountRecordsResponse(BaseModel):
    id: int
    account: str
    account_password: str
    auxiliary_email: Optional[str] = None
    two_fa: Optional[str] = None
    hubstudio_container_id: Optional[str] = None
    createtime: datetime
    updatetime: datetime
    init_account_time: Optional[datetime] = None
    status: Optional[str] = None
    account_type: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class AccountRecordsCreate(BaseModel):
    account: str
    account_password: str
    auxiliary_email: Optional[str] = None
    two_fa: Optional[str] = None
    hubstudio_container_id: Optional[str] = None
    init_account_time: Optional[datetime] = None
    status: Optional[str] = "active"
    account_type: Optional[str] = None
    user_name: Optional[str] = None

class ChangeLogResponse(BaseModel):
    id: int
    table_name: str
    field: str
    change_content: Optional[str] = None
    createtime: datetime
    
    class Config:
        from_attributes = True

class ChangeLogCreate(BaseModel):
    table_name: str
    field: str
    change_content: Optional[str] = None

class OperationLogResponse(BaseModel):
    id: int
    account_id: int
    date_time: datetime
    operation_json: dict
    createtime: datetime
    
    class Config:
        from_attributes = True

class OperationLogCreate(BaseModel):
    account_id: int
    datetime: datetime
    operation_json: dict

# FastAPI应用
app = FastAPI(title="Proxy User Management System", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 模板配置
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# 创建templates目录
os.makedirs("templates", exist_ok=True)

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 生成随机用户名和密码
def generate_username(length=None):
    """生成随机用户名"""
    if length is None:
        length = config["user_generation"]["username_length"]
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_password(length=None):
    """生成随机密码"""
    if length is None:
        length = config["user_generation"]["password_length"]
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def ensure_unique_username(db: Session):
    """确保用户名唯一"""
    while True:
        username = generate_username()
        existing = db.query(ProxyModel).filter(ProxyModel.username == username).first()
        if not existing:
            return username# 

# 解析YAML文件中的proxies
def parse_yaml_proxies(yaml_content: str):
    """解析YAML文件中的proxies配置"""
    try:
        data = yaml.safe_load(yaml_content)
        proxies = data.get('proxies', [])
        return proxies
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML解析错误: {str(e)}")

# API路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """主页 - 显示上传表单和数据列表"""
    return templates.TemplateResponse("index.html", {"request": request})

class AccountsUpload(BaseModel):
    accounts_data: str

@app.post("/upload-accounts/")
async def upload_accounts(
    accounts_upload: AccountsUpload,
    db: Session = Depends(get_db)
):
    """批量上传账号信息"""
    try:
        accounts_data = accounts_upload.accounts_data.strip()
        lines = accounts_data.split('\n')
        
        created_accounts = []
        skipped_accounts = []
        error_lines = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:  # 跳过空行
                continue
                
            # 使用----分割
            parts = line.split('----')
            if len(parts) != 3:
                error_lines.append(f"第{line_num}行: {line}")
                continue
                
            account, password, auxiliary_email = [part.strip() for part in parts]
            
            if not account or not password:
                error_lines.append(f"第{line_num}行: {line} (账号或密码为空)")
                continue
            
            # 检查账号是否已存在
            existing_account = db.query(AccountRecordsModel).filter(
                AccountRecordsModel.account == account
            ).first()
            
            if existing_account:
                skipped_accounts.append(account)
                continue
            
            # 创建新账号记录
            account_record = AccountRecordsModel(
                account=account,
                account_password=password,
                auxiliary_email=auxiliary_email if auxiliary_email else None,
                status="active"
            )
            
            db.add(account_record)
            created_accounts.append({
                'account': account,
                'auxiliary_email': auxiliary_email
            })
        
        db.commit()
        
        total_processed = len(created_accounts) + len(skipped_accounts) + len(error_lines)
        message = f"处理完成: 新增 {len(created_accounts)} 个账号, 跳过 {len(skipped_accounts)} 个重复账号, {len(error_lines)} 个格式错误"
        
        return JSONResponse({
            "message": message,
            "created_accounts": created_accounts,
            "skipped_accounts": skipped_accounts,
            "error_lines": error_lines,
            "total_processed": total_processed
        })
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"处理账号数据时出错: {str(e)}")

@app.post("/upload-yaml/")
async def upload_yaml(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    department_id: str = Form(""),
    db: Session = Depends(get_db)
):
    """上传YAML文件并解析proxies"""
    if not file.filename.endswith(('.yaml', '.yml')):
        raise HTTPException(status_code=400, detail="请上传YAML文件")
    
    try:
        content = await file.read()
        yaml_content = content.decode('utf-8')
        proxies = parse_yaml_proxies(yaml_content)
        
        created_proxies = []
        updated_proxies = []
        
        for proxy_config in proxies[3:]:    # 从第4个开始 ，前3个是机场的额外信息
            # 清理name中的空格
            clean_name = proxy_config.get('name', '').strip(' ')
            # 有些机场有四个配置信息，还要额外跳过
            if "剩余流量" in clean_name or "距离下次" in clean_name or "到期" in clean_name:
                continue
            
            proxy_config['name'] = clean_name
            proxy_str = str(proxy_config)
            proxy_name = clean_name
            
            # 检查是否存在相同的proxy_name + source_type的记录
            existing_proxy = db.query(ProxyModel).filter(
                ProxyModel.proxy_name == proxy_name,
                ProxyModel.source_type == source_type
            ).first()
            
            if existing_proxy:
                # 更新现有记录
                existing_proxy.before_update = existing_proxy.proxy  # 保存更新前的配置
                existing_proxy.proxy = proxy_str  # 更新proxy配置
                existing_proxy.department_id = department_id  # 更新部门ID
                existing_proxy.updatetime = datetime.now()  # 更新时间
                
                updated_proxies.append({
                    'proxy_name': existing_proxy.proxy_name,
                    'username': existing_proxy.username,
                    'password': existing_proxy.password,
                    'action': 'updated'
                })
            else:
                # 创建新记录
                username = ensure_unique_username(db)
                password = generate_password()
                
                proxy_record = ProxyModel(
                    proxy_name=proxy_name,
                    proxy=proxy_str,
                    source_type=source_type,
                    username=username,
                    password=password,
                    department_id=department_id
                )
                
                db.add(proxy_record)
                created_proxies.append({
                    'proxy_name': proxy_record.proxy_name,
                    'username': username,
                    'password': password,
                    'action': 'created'
                })
        
        db.commit()
        
        total_processed = len(created_proxies) + len(updated_proxies)
        message = f"处理完成: 新增 {len(created_proxies)} 个节点, 更新 {len(updated_proxies)} 个节点"
        
        return JSONResponse({
            "message": message,
            "created_proxies": created_proxies,
            "updated_proxies": updated_proxies,
            "total_processed": total_processed
        })
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"处理文件时出错: {str(e)}")

@app.get("/proxies/", response_model=List[ProxyResponse])
async def get_proxies(
    page: int = 1,
    size: int = 10,
    source_type: Optional[str] = None,
    department_id: Optional[str] = None,
    source_type_options: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取代理列表（分页）"""
    query = db.query(ProxyModel)
    
    # 过滤条件
    if source_type:
        query = query.filter(ProxyModel.source_type == source_type)
    if department_id:
        query = query.filter(ProxyModel.department_id == department_id)

    if source_type_options:
        query = query.filter(ProxyModel.source_type == source_type_options)
    
    # 分页
    offset = (page - 1) * size
    proxies = query.offset(offset).limit(size).all()
    
    return proxies

@app.get("/proxies/count")
async def get_proxies_count(
    source_type: Optional[str] = None,
    department_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取代理总数"""
    query = db.query(ProxyModel)
    
    if source_type:
        query = query.filter(ProxyModel.source_type == source_type)
    if department_id:
        query = query.filter(ProxyModel.department_id == department_id)
    
    count = query.count()
    return {"count": count}

@app.delete("/proxies/{proxy_id}")
async def delete_proxy(proxy_id: int, db: Session = Depends(get_db)):
    """删除代理"""
    proxy = db.query(ProxyModel).filter(ProxyModel.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="代理不存在")
    
    db.delete(proxy)
    db.commit()
    return {"message": "代理删除成功"}

@app.get("/ui", response_class=HTMLResponse)
async def proxy_ui(request: Request):
    """代理管理UI界面"""
    return templates.TemplateResponse("proxy_ui.html", {"request": request})

@app.get("/config-ui", response_class=HTMLResponse)
async def config_ui(request: Request):
    """配置管理UI界面"""
    return templates.TemplateResponse("config.html", {"request": request})

@app.get("/generate-config")
async def generate_clash_config(db: Session = Depends(get_db)):
    """生成clash-meta配置文件"""
    try:
        # 查询所有department不为空的记录
        proxies_data = db.query(ProxyModel).filter(
            ProxyModel.department_id != "",
            ProxyModel.department_id.isnot(None)
        ).all()
        
        if not proxies_data:
            raise HTTPException(status_code=404, detail="没有找到有效的代理数据")
        
        # 构建配置文件结构
        clash_config = {
            "mixed-port": 7891,
            "allow-lan": True,
            "external-controller": "0.0.0.0:9093",
            "bind-address": "*",
            "mode": "rule",
            "log-level": "info",
            "ipv6": False,
            "department-secrets": config["departments"],
            "profile": {
                "store-selected": True,
                "tracing": False,
                "store-fake-ip": False
            },
            "unified-delay": True,
            "dns": {
                "enable": True,
                "ipv6": False,
                "listen": "0.0.0.0:1053",
                "enhanced-mode": "fake-ip",
                "fake-ip-range": "198.18.0.1/16",
                "use-hosts": True,
                "default-nameserver": ["223.5.5.5"],
                "nameserver": [
                    "119.29.29.29",
                    "223.5.5.5",
                    "https://dns.alidns.com/dns-query",
                    "https://doh.pub/dns-query",
                    "114.114.114.114",
                    "156.154.70.1",
                    "1.0.0.1",
                    "8.8.4.4"
                ],
                "fake-ip-filter": [
                    "*.lan",
                    "localhost.ptlogin2.qq.com",
                    "dns.msftncsi.com"
                ],
                "fallback": [
                        '208.67.222.222:5353',
                        '208.67.220.220:5353',
                        '208.67.222.220:5353',
                        '208.67.220.222:5353',
                        'https://1.1.1.1/dns-query',
                        'https://1.1.1.2/dns-query',
                        'https://1.1.1.3/dns-query',
                        'https://1.0.0.1/dns-query',
                        'https://1.0.0.2/dns-query',
                        'https://1.0.0.3/dns-query',
                        'https://45.11.45.11/dns-query',
                        'https://146.112.41.2/dns-query',
                        'https://162.159.36.1/dns-query',
                        'https://162.159.46.1/dns-query',
                        'https://9.9.9.11:5053/dns-query',
                        'https://101.6.6.6:8443/dns-query',
                        'https://208.67.222.222/dns-query',
                        'https://208.67.220.220/dns-query',
                        'https://185.222.222.222/dns-query',
                        'https://101.101.101.101/dns-query',
                        'https://149.112.112.11:5053/dns-query'
                ],
                "fallback-filter": {
                    "geoip": True,
                    "geoip-code": "CN",
                    "ipcidr": ["240.0.0.0/4"]
                }
            },
            "proxies": [],
            "authentication": [],
            # 放行本地调用，用于用户操作日志收集
            "rules": [
                "IP-CIDR,192.168.132.58/32,DIRECT",
            ]
        }
        
        # 处理proxies数据
        for proxy_data in proxies_data:
            try:
                # 解析proxy字段中的配置
                if isinstance(proxy_data.proxy, str):
                    # 如果是字符串，尝试解析为字典
                    try:
                        proxy_config = eval(proxy_data.proxy)
                    except:
                        # 如果eval失败，尝试yaml解析
                        proxy_config = yaml.safe_load(proxy_data.proxy)
                else:
                    proxy_config = proxy_data.proxy
                
                clash_config["proxies"].append(proxy_config)
                
                # 添加authentication
                auth_entry = f"{proxy_data.username}:{proxy_data.password}"
                clash_config["authentication"].append(auth_entry)
                
                # 添加rules
                rule_entry = f"PROXY-USER,{proxy_data.username},{proxy_config.get('name', proxy_data.proxy_name)}"
                clash_config["rules"].append(rule_entry)
                
            except Exception as e:
                print(f"处理代理配置时出错: {e}, proxy_data: {proxy_data.proxy}")
                continue
        
        # 转换为YAML格式
        yaml_content = yaml.dump(clash_config, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return {
            "message": f"成功生成配置文件，包含 {len(clash_config['proxies'])} 个代理节点",
            "config": yaml_content,
            "proxy_count": len(clash_config["proxies"]),
            "user_count": len(clash_config["authentication"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成配置文件时出错: {str(e)}")

@app.get("/download-config")
async def download_clash_config(db: Session = Depends(get_db)):
    """下载clash-meta配置文件"""
    from fastapi.responses import Response
    
    try:
        # 获取配置内容
        config_response = await generate_clash_config(db)
        yaml_content = config_response["config"]
        
        # 返回文件下载响应
        return Response(
            content=yaml_content,
            media_type="application/x-yaml",
            headers={"Content-Disposition": "attachment; filename=clash_config.yaml"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载配置文件时出错: {str(e)}")

# Account Records API路由
@app.post("/account-records/", response_model=AccountRecordsResponse)
async def create_account_record(
    account_data: AccountRecordsCreate,
    db: Session = Depends(get_db)
):
    """创建账号记录"""
    account_record = AccountRecordsModel(
        account=account_data.account,
        account_password=account_data.account_password,
        auxiliary_email=account_data.auxiliary_email,
        two_fa=account_data.two_fa,
        hubstudio_container_id=account_data.hubstudio_container_id,
        init_account_time=account_data.init_account_time,
        status=account_data.status,
        account_type=account_data.account_type,
        user_name=account_data.user_name
    )
    
    db.add(account_record)
    db.commit()
    db.refresh(account_record)
    return account_record

@app.get("/account-records/", response_model=List[AccountRecordsResponse])
async def get_account_records(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    """获取账号记录列表（分页）"""
    offset = (page - 1) * size
    records = db.query(AccountRecordsModel).offset(offset).limit(size).all()
    return records

@app.get("/account-records/{record_id}", response_model=AccountRecordsResponse)
async def get_account_record(record_id: int, db: Session = Depends(get_db)):
    """获取单个账号记录"""
    record = db.query(AccountRecordsModel).filter(AccountRecordsModel.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="账号记录不存在")
    return record

@app.put("/account-records/{record_id}", response_model=AccountRecordsResponse)
async def update_account_record(
    record_id: int,
    account_data: AccountRecordsCreate,
    db: Session = Depends(get_db)
):
    """更新账号记录"""
    record = db.query(AccountRecordsModel).filter(AccountRecordsModel.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="账号记录不存在")
    
    record.account = account_data.account
    record.account_password = account_data.account_password
    record.auxiliary_email = account_data.auxiliary_email
    record.two_fa = account_data.two_fa
    record.hubstudio_container_id = account_data.hubstudio_container_id
    record.init_account_time = account_data.init_account_time
    record.status = account_data.status
    record.account_type = account_data.account_type
    record.user_name = account_data.user_name
    
    db.commit()
    db.refresh(record)
    return record

@app.delete("/account-records/{record_id}")
async def delete_account_record(record_id: int, db: Session = Depends(get_db)):
    """删除账号记录"""
    record = db.query(AccountRecordsModel).filter(AccountRecordsModel.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="账号记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "账号记录删除成功"}

@app.get("/account-records/count")
async def get_account_records_count(db: Session = Depends(get_db)):
    """获取账号记录总数"""
    count = db.query(AccountRecordsModel).count()
    return {"count": count}

# Change Log API路由
@app.post("/change-logs/", response_model=ChangeLogResponse)
async def create_change_log(
    change_data: ChangeLogCreate,
    db: Session = Depends(get_db)
):
    """创建变更记录"""
    change_log = ChangeLogModel(
        table_name=change_data.table_name,
        field=change_data.field,
        change_content=change_data.change_content
    )
    
    db.add(change_log)
    db.commit()
    db.refresh(change_log)
    return change_log

@app.get("/change-logs/", response_model=List[ChangeLogResponse])
async def get_change_logs(
    page: int = 1,
    size: int = 10,
    table_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取变更记录列表（分页）"""
    query = db.query(ChangeLogModel)
    
    if table_name:
        query = query.filter(ChangeLogModel.table_name == table_name)
    
    offset = (page - 1) * size
    logs = query.order_by(ChangeLogModel.createtime.desc()).offset(offset).limit(size).all()
    return logs

@app.get("/change-logs/{log_id}", response_model=ChangeLogResponse)
async def get_change_log(log_id: int, db: Session = Depends(get_db)):
    """获取单个变更记录"""
    log = db.query(ChangeLogModel).filter(ChangeLogModel.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="变更记录不存在")
    return log

@app.delete("/change-logs/{log_id}")
async def delete_change_log(log_id: int, db: Session = Depends(get_db)):
    """删除变更记录"""
    log = db.query(ChangeLogModel).filter(ChangeLogModel.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="变更记录不存在")
    
    db.delete(log)
    db.commit()
    return {"message": "变更记录删除成功"}

@app.get("/change-logs/count")
async def get_change_logs_count(
    table_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取变更记录总数"""
    query = db.query(ChangeLogModel)
    
    if table_name:
        query = query.filter(ChangeLogModel.table_name == table_name)
    
    count = query.count()
    return {"count": count}

# Operation Log API路由
@app.post("/operation-logs/", response_model=OperationLogResponse)
async def create_operation_log(
    operation_data: OperationLogCreate,
    db: Session = Depends(get_db)
):
    """创建操作日志"""
    # 验证account_id是否存在
    account_record = db.query(AccountRecordsModel).filter(AccountRecordsModel.id == operation_data.account_id).first()
    if not account_record:
        raise HTTPException(status_code=404, detail="账号记录不存在")
    
    operation_log = OperationLogModel(
        account_id=operation_data.account_id,
        date_time=operation_data.datetime,
        operation_json=operation_data.operation_json
    )
    
    db.add(operation_log)
    db.commit()
    db.refresh(operation_log)
    return operation_log

@app.get("/config")
async def get_config():
    """获取当前配置"""
    return config

@app.post("/config")
async def update_config(new_config: dict):
    """更新配置文件"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.yaml")
        
        # 更新内存中的配置
        global config
        config.update(new_config)
        
        # 保存到文件
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        return {"message": "配置更新成功", "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")

@app.post("/update-clash-config")
async def update_clash_config(db: Session = Depends(get_db)):
    """更新clash-meta配置"""
    import os
    import requests
    
    try:
        # 1. 生成最新的配置文件
        config_response = await generate_clash_config(db)
        yaml_content = config_response["config"]
        
        # 2. 保存配置文件到clash-meta允许的目录
        # 使用用户配置目录，这是clash-meta允许的安全路径
        config_dir = os.path.expanduser(config["config_paths"]["clash_config_dir"])
        os.makedirs(config_dir, exist_ok=True)
        config_file_path = os.path.join(config_dir, config["config_paths"]["clash_config_filename"])
        
        with open(config_file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        # 3. 调用clash-meta的配置更新API
        clash_api_url = config["clash_meta"]["api_url"] + config["clash_meta"]["config_endpoint"]
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config["clash_meta"]["auth_token"]}'
        }
        
        payload = {
            "path": config_file_path
        }
        
        response = requests.put(clash_api_url, json=payload, headers=headers, timeout=config["clash_meta"]["timeout"])
        print(response.text)
        if response.status_code in [200, 204]:
            return {
                "message": "Clash配置更新成功",
                "config_path": config_file_path,
                "proxy_count": config_response["proxy_count"],
                "user_count": config_response["user_count"]
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"更新Clash配置失败: HTTP {response.status_code} - {response.text}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, 
            detail=f"无法连接到Clash API ({config['clash_meta']['api_url']}): {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新Clash配置时出错: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config["server"]["host"], port=config["server"]["port"])