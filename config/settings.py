from pydantic_settings import BaseSettings
from config.env import load_env_config
import os

# 加载环境配置
loaded_files = load_env_config()

class Settings(BaseSettings):
    MAX_RECORDS_PER_REQUEST: int = int(os.getenv('MAX_RECORDS_PER_REQUEST', 10000))
    MAX_TOTAL_RECORDS: int = int(os.getenv('MAX_TOTAL_RECORDS', 100000))
    LARGE_REQUEST_TIMEOUT: int = int(os.getenv('LARGE_REQUEST_TIMEOUT', 300))

    class Config:
        env_file = ['.env', '.env.prod' if os.getenv('ENV') == 'prod' else '.env.local']
        env_file_encoding = 'utf-8'