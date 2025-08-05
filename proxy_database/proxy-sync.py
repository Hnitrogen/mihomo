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
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import yaml
import random
import string
import os
from typing import List, Optional
from pydantic import BaseModel

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./proxy_database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库模型
class ProxyModel(Base):
    __tablename__ = "proxy"
    
    id = Column(Integer, primary_key=True, index=True)
    proxy_name = Column(String, index=True)  # 节点名称
    proxy = Column(Text)  # 机场config行
    source_type = Column(String)  # 机场名
    username = Column(String, unique=True, index=True)  # userProxy账号
    password = Column(String)  # userProxy密码
    department_id = Column(String)  # 部门id
    before_update = Column(Text)  # 更新前的proxy配置
    updatetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    createtime = Column(DateTime, default=datetime.now)

# 数据库迁移函数
def migrate_database():
    """检查并添加新字段"""
    try:
        # 尝试查询before_update字段，如果不存在会抛出异常
        db = SessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT before_update FROM proxy LIMIT 1"))
        db.close()
        print("数据库字段已存在，无需迁移")
    except Exception:
        # 字段不存在，添加字段
        try:
            db = SessionLocal()
            from sqlalchemy import text
            db.execute(text("ALTER TABLE proxy ADD COLUMN before_update TEXT"))
            db.commit()
            db.close()
            print("成功添加before_update字段")
        except Exception as e:
            print(f"添加字段失败: {e}")

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
    updatetime: datetime
    createtime: datetime
    
    class Config:
        from_attributes = True

class ProxyCreate(BaseModel):
    source_type: str
    department_id: str

# FastAPI应用
app = FastAPI(title="Proxy User Management System", version="1.0.0")

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
def generate_username(length=6):
    """生成6位随机用户名"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_password(length=12):
    """生成12位随机密码"""
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
        
        for proxy_config in proxies:
            proxy_name = proxy_config.get('name', '')
            proxy_str = str(proxy_config)
            
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
    db: Session = Depends(get_db)
):
    """获取代理列表（分页）"""
    query = db.query(ProxyModel)
    
    # 过滤条件
    if source_type:
        query = query.filter(ProxyModel.source_type == source_type)
    if department_id:
        query = query.filter(ProxyModel.department_id == department_id)
    
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
        config = {
            "mixed-port": 7891,
            "allow-lan": True,
            "external-controller": "0.0.0.0:9093",
            "bind-address": "*",
            "mode": "rule",
            "log-level": "info",
            "ipv6": False,
            "department-secrets": {
                "1": "tech_dept",
                "2": "sales_dept", 
                "3": "hr_dept",
                "4": "finance_dept"
            },
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
                    "https://doh.pub/dns-query",
                    "https://dns.alidns.com/dns-query"
                ],
                "fake-ip-filter": [
                    "*.lan",
                    "localhost.ptlogin2.qq.com",
                    "dns.msftncsi.com"
                ],
                "fallback": ["1.1.1.1", "8.8.8.8"],
                "fallback-filter": {
                    "geoip": True,
                    "geoip-code": "CN",
                    "ipcidr": ["240.0.0.0/4"]
                }
            },
            "proxies": [],
            "authentication": [],
            "rules": []
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
                
                config["proxies"].append(proxy_config)
                
                # 添加authentication
                auth_entry = f"{proxy_data.username}:{proxy_data.password}"
                config["authentication"].append(auth_entry)
                
                # 添加rules
                rule_entry = f"PROXY-USER,{proxy_data.username},{proxy_config.get('name', proxy_data.proxy_name)}"
                config["rules"].append(rule_entry)
                
            except Exception as e:
                print(f"处理代理配置时出错: {e}, proxy_data: {proxy_data.proxy}")
                continue
        
        # 转换为YAML格式
        yaml_content = yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return {
            "message": f"成功生成配置文件，包含 {len(config['proxies'])} 个代理节点",
            "config": yaml_content,
            "proxy_count": len(config["proxies"]),
            "user_count": len(config["authentication"])
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
        config_dir = os.path.expanduser("~/.config/mihomo")
        os.makedirs(config_dir, exist_ok=True)
        config_file_path = os.path.join(config_dir, "aggregated_clash_config.yaml")
        
        with open(config_file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        # 3. 调用clash-meta的配置更新API
        clash_api_url = "http://192.168.132.58:9093/configs"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer seo-pinkman'
        }
        
        payload = {
            "path": config_file_path
        }
        
        response = requests.put(clash_api_url, json=payload, headers=headers, timeout=10)
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
            detail=f"无法连接到Clash API (http://192.168.132.58:9093): {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新Clash配置时出错: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8202)