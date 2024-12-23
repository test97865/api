from pydantic_settings import BaseSettings
import logging
import os
from config.env import load_env_config

logger = logging.getLogger(__name__)

# 加载环境配置
loaded_files = load_env_config()
logger.info(f"已加载的环境配置文件: {loaded_files}")

class AuthSettings(BaseSettings):
    API_KEY: str = os.getenv('XAPI_API_KEY', 'test')  # 默认值为 'test'
    
    class Config:
        env_prefix = "XAPI_"
        populate_by_name = True

    def get_api_keys(self) -> list[str]:
        """获取 API keys 列表"""
        api_key = self.API_KEY
        if not api_key:
            logger.warning("未找到有效的 API key")
            return []
            
        keys = [k.strip() for k in api_key.split(',') if k.strip()]
        logger.info(f"有效的 API keys: {keys}")
        return keys

# 创建设置实例
auth_settings = AuthSettings()
