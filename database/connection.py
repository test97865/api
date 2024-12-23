import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import mysql.connector
from mysql.connector import Error
from supabase import create_client, Client
import logging
from config.database import MYSQL_CONFIG, SUPABASE_CONFIG
from typing import Optional, Any

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.mysql_conn = None
        self.supabase_client = None
        self._current_connection = None  # 新增：跟踪当前使用的连接
        self._initialize_connection()

    def _initialize_connection(self):
        """初始化数据库连接，优先尝试 Supabase，失败则使用 MySQL"""
        if SUPABASE_CONFIG and self._try_supabase_connection():
            logger.info("成功连接到 Supabase")
            self._current_connection = 'supabase'
        elif self._try_mysql_connection():
            logger.info("成功连接到 MySQL")
            self._current_connection = 'mysql'
        else:
            raise ConnectionError("无法连接到任何数据库")

    def _try_mysql_connection(self) -> bool:
        """尝试连接 MySQL"""
        try:
            self.mysql_conn = mysql.connector.connect(
                **MYSQL_CONFIG,
                charset='utf8mb4',
                use_unicode=True
            )
            return self.mysql_conn.is_connected()
        except Error as e:
            logger.error(f"MySQL 连接失败: {str(e)}")
            return False

    def _try_supabase_connection(self) -> bool:
        """尝试连接 Supabase"""
        if not SUPABASE_CONFIG:
            return False
        try:
            self.supabase_client = create_client(
                SUPABASE_CONFIG['url'],
                SUPABASE_CONFIG['key']
            )
            # 测试连接
            self.supabase_client.table(SUPABASE_CONFIG['table']).select("*").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase 连接失败: {str(e)}")
            return False

    def get_connection(self):
        """获取当前活动的数据库连接"""
        if self._current_connection == 'supabase':
            return self.supabase_client
        elif self._current_connection == 'mysql':
            return self.mysql_conn
        return None

    def close(self):
        """关闭所有数据库连接"""
        if self.mysql_conn and self.mysql_conn.is_connected():
            self.mysql_conn.close()
        # Supabase client 不需要显式关闭

# 全局数据库连接实例
db_connection = None

def get_db():
    """获取数据库连接的单例实例"""
    global db_connection
    if db_connection is None:
        db_connection = DatabaseConnection()
    return db_connection

if __name__ == "__main__":
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        if conn:
            print("数据库连接成功！")
            if isinstance(conn, Client):
                print("使用 Supabase 连接")
            else:
                print("使用 MySQL 连接")
        db.close()
    except Exception as e:
        print(f"数据库连接失败：{str(e)}") 