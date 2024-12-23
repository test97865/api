import os
from config.env import load_env_config
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# 加载环境配置
load_env_config()

class DatabaseConfig:
    @staticmethod
    def get_mysql_config() -> Dict[str, any]:
        return {
            'database': os.getenv('DB_NAME', 'assets'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306))
        }

    @staticmethod
    def get_supabase_config() -> Optional[Dict[str, str]]:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not all([url, key]):
            logger.warning("Supabase 配置不完整，将使用 MySQL 作为默认数据库")
            return None
            
        return {
            'url': url,
            'key': key,
            'table': os.getenv('SUPABASE_TABLE', 'assets')
        }

# 实例化配置
MYSQL_CONFIG = DatabaseConfig.get_mysql_config()
SUPABASE_CONFIG = DatabaseConfig.get_supabase_config()

# 日志输出当前配置
logger.info(f"MySQL 主机: {MYSQL_CONFIG['host']}")
if SUPABASE_CONFIG:
    logger.info(f"Supabase URL: {SUPABASE_CONFIG['url']}")