"""
数据库连接 + 表初始化
参考：系统设计说明书 7.3 数据初始化脚本
"""

import sqlite3
from pathlib import Path

from config import DATABASE_PATH

SCHEMA_SQL = Path(__file__).resolve().parent / "schema.sql"


def get_db() -> sqlite3.Connection:
    """获取数据库连接（每个请求一个连接，调用方负责关闭）"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row     # 让查询结果支持 dict 风格访问
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """应用启动时调用，创建表 + 预置数据。数据库已存在时跳过"""
    if not DATABASE_PATH.exists():
        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
        conn.commit()
        conn.close()
        print(f"[OK] 数据库已初始化: {DATABASE_PATH}")
    else:
        print(f"[OK] 数据库已存在: {DATABASE_PATH}")
