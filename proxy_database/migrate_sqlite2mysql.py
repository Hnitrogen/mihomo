import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

# ======== 配置区 ========
sqlite_file = r"C:\\Users\\pc\\Desktop\work\\mihomo\\proxy_database\\proxy_database.db"  # SQLite 文件路径
mysql_user = "root"       # MySQL 用户名
mysql_password = "7212"   # MySQL 密码
mysql_host = "localhost"  # MySQL 主机
mysql_db = "ugc"       # MySQL 数据库名
mysql_port = 3306         # MySQL 端口
# =======================

# 1. 连接 SQLite
sqlite_conn = sqlite3.connect(sqlite_file)

# 2. 连接 MySQL（utf8mb4 确保中文）
mysql_engine = create_engine(
    f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4"
)

# 3. 在 MySQL 中创建 proxy 表（按你给的 DDL）
create_table_sql = """
CREATE TABLE IF NOT EXISTS proxy (
    id INT NOT NULL,
    proxy_name VARCHAR(255),
    proxy TEXT,
    source_type VARCHAR(255),
    username VARCHAR(255),
    password VARCHAR(255),
    department_id VARCHAR(255),
    updatetime DATETIME,
    createtime DATETIME,
    before_update TEXT,
    PRIMARY KEY (id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"""

with mysql_engine.connect() as conn:
    conn.execute(text(create_table_sql))
    
    # 检查并创建索引（兼容旧版本MySQL）
    # 检查索引是否存在的函数
    def index_exists(connection, table_name, index_name):
        result = connection.execute(text("""
            SELECT COUNT(*) as count FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = :table_name 
            AND INDEX_NAME = :index_name
        """), {"table_name": table_name, "index_name": index_name})
        return result.fetchone()[0] > 0
    
    # 创建索引（如果不存在）
    if not index_exists(conn, "proxy", "ix_proxy_proxy_name"):
        conn.execute(text("CREATE INDEX ix_proxy_proxy_name ON proxy (proxy_name);"))
        print("创建索引: ix_proxy_proxy_name")
    
    if not index_exists(conn, "proxy", "ix_proxy_id"):
        conn.execute(text("CREATE INDEX ix_proxy_id ON proxy (id);"))
        print("创建索引: ix_proxy_id")
    
    if not index_exists(conn, "proxy", "ix_proxy_username"):
        conn.execute(text("CREATE UNIQUE INDEX ix_proxy_username ON proxy (username);"))
        print("创建唯一索引: ix_proxy_username")
    
    conn.commit()

# 4. 读取 SQLite 中的 proxy 表
df = pd.read_sql("SELECT * FROM proxy", sqlite_conn)

# 5. 写入 MySQL（替换已有数据）
df.to_sql("proxy", mysql_engine, if_exists="replace", index=False)

print("✅ proxy 表迁移完成！")

sqlite_conn.close()
