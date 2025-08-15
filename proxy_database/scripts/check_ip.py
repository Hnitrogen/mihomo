"""
脚本文件：用于刷写Proxy中的 ip,before_ip 等字段

proxy表中存在机场节点以及UserProxy信息，
通过Proxy表中的username + password 可以完成clash-meta代理使用，你需要
请求如https://ipinfo.io/ 网站，获取的对应的ip信息，国家信息
"""

import requests
import json
import time
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# ======== 配置区 ========
mysql_user = "root"
mysql_password = "7212"
mysql_host = "localhost"
mysql_db = "ugc"
mysql_port = 3306
clash_proxy_url = "http://192.168.132.58:7891"  # Clash-Meta代理地址
# 现在使用 ipinfo.io 获取IP信息，无需API密钥
# =======================

Base = declarative_base()

class ProxyModel(Base):
    __tablename__ = "proxy"
    
    id = Column(Integer, primary_key=True, index=True)
    proxy_name = Column(String(255), index=True)
    proxy = Column(Text)
    source_type = Column(String(100))
    username = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    department_id = Column(String(50))
    before_update = Column(Text)
    ip = Column(String(45))
    before_ip = Column(String(45))
    country = Column(String(100))
    status = Column(String(50))
    ip_check_data = Column(JSON)
    updatetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    createtime = Column(DateTime, default=datetime.now)

# 创建数据库连接
engine = create_engine(
    f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4"
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_proxy_ip_info(username, password):
    """
    通过代理获取IP信息（使用ipinfo.io）
    """
    try:
        # 将用户名和密码直接嵌入到代理URL中
        proxy_url = f"http://{username}:{password}@192.168.132.58:7891"
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        print(f"使用代理: {username}:{password}@192.168.132.58:7891")
        
        # 使用ipinfo.io获取IP信息
        response = requests.get(
            "http://ipinfo.io/json",
            proxies=proxies,
            timeout=30
        )

        print(response.text)
        
        if response.status_code == 200:
            ip_data = response.json()
            return ip_data
        else:
            print(f"❌ 获取IP失败，状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return None



def check_proxy_ip(username, password):
    """
    通过代理检查IP信息（使用ipinfo.io）
    """
    # 获取代理的IP信息
    ip_data = get_proxy_ip_info(username, password)
    if not ip_data:
        return None
    
    ip_address = ip_data.get('ip', '')
    print(f"🌐 检测到代理IP: {ip_address}")
    
    # 解析ipinfo.io的响应数据
    # 解析经纬度坐标
    loc = ip_data.get('loc', '')
    latitude, longitude = None, None
    if loc and ',' in loc:
        try:
            lat_str, lon_str = loc.split(',')
            latitude = float(lat_str.strip())
            longitude = float(lon_str.strip())
        except (ValueError, IndexError):
            pass
    
    # 整合信息，保持与原有格式兼容
    result = {
        'ip': ip_address,
        'country': ip_data.get('country', ''),  # 国家代码，如 "HK"
        'country_name': ip_data.get('country', ''),  # ipinfo.io只提供代码，这里复用
        'city': ip_data.get('city', ''),
        'region': ip_data.get('region', ''),
        'timezone': ip_data.get('timezone', ''),
        'latitude': latitude,
        'longitude': longitude,
        'postal': ip_data.get('postal', ''),
        'org': ip_data.get('org', ''),  # 组织信息
        'provider': ip_data.get('org', ''),  # 复用org作为provider
        'organisation': ip_data.get('org', ''),
        'raw_ipinfo_data': ip_data  # 保存原始ipinfo数据
    }
    
    return result

def update_proxy_ip_info():
    """
    更新所有代理的IP信息
    """
    db = SessionLocal()
    try:
        # 获取所有有用户名和密码的代理记录
        proxies = db.query(ProxyModel).filter(
            ProxyModel.username.isnot(None),
            ProxyModel.password.isnot(None)
        ).all()
        
        print(f"📊 找到 {len(proxies)} 个代理记录需要检查")
        
        success_count = 0
        failed_count = 0
        
        for proxy in proxies:
            print(f"\n🔍 检查代理: {proxy.proxy_name} (用户: {proxy.username})")
            
            # 检查IP信息
            ip_info = check_proxy_ip(proxy.username, proxy.password)
            
            if ip_info:
                new_ip = ip_info.get('ip')
                country = ip_info.get('country')
                country_name = ip_info.get('country_name', ip_info.get('country'))
                city = ip_info.get('city')
                org = ip_info.get('org')
                
                # 如果IP发生变化，将旧IP移到before_ip
                if proxy.ip and proxy.ip != new_ip:
                    proxy.before_ip = proxy.ip
                    print(f"📝 IP变化: {proxy.ip} -> {new_ip}")
                
                # 更新IP信息
                proxy.ip = new_ip
                proxy.country = country
                proxy.status = "active"
                proxy.ip_check_data = ip_info
                proxy.updatetime = datetime.now()
                
                print(f"✅ 更新成功: IP={new_ip}, 国家={country_name}({country}), 城市={city}, 组织={org}")
                success_count += 1
                
            else:
                proxy.status = "failed"
                proxy.updatetime = datetime.now()
                print(f"❌ 检查失败")
                failed_count += 1
            
            # 提交单个记录的更新
            try:
                db.commit()
            except SQLAlchemyError as e:
                print(f"❌ 数据库更新失败: {e}")
                db.rollback()
                failed_count += 1
            
            # 避免请求过于频繁
            time.sleep(2)
        
        print(f"\n📈 检查完成: 成功 {success_count} 个, 失败 {failed_count} 个")
        
    except Exception as e:
        print(f"❌ 程序执行异常: {e}")
        db.rollback()
    finally:
        db.close()

def check_single_proxy(proxy_id):
    """
    检查单个代理的IP信息
    """
    db = SessionLocal()
    try:
        proxy = db.query(ProxyModel).filter(ProxyModel.id == proxy_id).first()
        
        if not proxy:
            print(f"❌ 未找到ID为 {proxy_id} 的代理记录")
            return
        
        if not proxy.username or not proxy.password:
            print(f"❌ 代理记录缺少用户名或密码")
            return
        
        print(f"🔍 检查代理: {proxy.proxy_name} (用户: {proxy.username})")
        
        ip_info = check_proxy_ip(proxy.username, proxy.password)
        
        if ip_info:
            new_ip = ip_info.get('ip')
            country = ip_info.get('country')
            country_name = ip_info.get('country_name', ip_info.get('country'))
            city = ip_info.get('city')
            org = ip_info.get('org')
            
            if proxy.ip and proxy.ip != new_ip:
                proxy.before_ip = proxy.ip
                print(f"📝 IP变化: {proxy.ip} -> {new_ip}")
            
            proxy.ip = new_ip
            proxy.country = country
            proxy.status = "active"
            proxy.ip_check_data = ip_info
            proxy.updatetime = datetime.now()
            
            db.commit()
            print(f"✅ 更新成功: IP={new_ip}, 国家={country_name}({country}), 城市={city}, 组织={org}")
        else:
            proxy.status = "failed"
            proxy.updatetime = datetime.now()
            db.commit()
            print(f"❌ 检查失败")
            
    except Exception as e:
        print(f"❌ 程序执行异常: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 检查单个代理
        try:
            proxy_id = int(sys.argv[1])
            check_single_proxy(proxy_id)
        except ValueError:
            print("❌ 请提供有效的代理ID")
    else:
        # 检查所有代理
        update_proxy_ip_info()


