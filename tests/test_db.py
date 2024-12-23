import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.connection import DatabaseConnection
from supabase import Client
import logging
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        if conn:
            logger.info("数据库连接成功！")
            if isinstance(conn, Client):
                logger.info("使用 Supabase 连接")
                # 测试查询
                result = conn.table('assets').select("*").limit(1).execute()
                logger.info(f"查询测试成功，获取到 {len(result.data)} 条记录")
                # 打印第一条记录
                if result.data:
                    logger.info(f"数据示例: {json.dumps(result.data[0], ensure_ascii=False, indent=2)}")
            else:
                logger.info("使用 MySQL 连接")
                cursor = conn.cursor(dictionary=True)  # 使用字典游标
                cursor.execute("SELECT * FROM assets LIMIT 1")
                result = cursor.fetchone()
                if result:
                    logger.info(f"数据示例: {json.dumps(result, ensure_ascii=False, indent=2)}")
                cursor.close()
        db.close()
    except Exception as e:
        logger.error(f"数据库连接失败：{str(e)}")
        raise

if __name__ == "__main__":
    test_database_connection() 