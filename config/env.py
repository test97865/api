import os
from dotenv import load_dotenv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self):
        self.env_files = {
            'common': '.env',
            'prod': '.env.prod',
            'local': '.env.local'
        }
    
    def has_env_files(self) -> bool:
        """检查是否存在任何环境配置文件"""
        return any(Path(file).exists() for file in self.env_files.values())
    
    def load_from_env_files(self):
        """从环境文件加载配置"""
        loaded_vars = {}
        
        # 首先加载通用配置
        if Path(self.env_files['common']).exists():
            logger.info(f"Loading variables from {self.env_files['common']}")
            load_dotenv(self.env_files['common'])
            
        # 然后根据环境加载特定配置
        env_file = self.env_files['prod'] if os.getenv('ENV') == 'prod' else self.env_files['local']
        if Path(env_file).exists():
            logger.info(f"Loading variables from {env_file}")
            load_dotenv(env_file, override=True)
                
        # 收集所有环境变量
        for key, value in os.environ.items():
            if not key.startswith(('PYTHON', 'PATH', 'LANG', 'HOME', 'SHELL')):
                loaded_vars[key] = value
                
        return loaded_vars
    
    def load_config(self):
        """统一的配置加载入口"""
        if self.has_env_files():
            logger.info("Found environment files, loading configuration from files")
            return self.load_from_env_files()
        else:
            logger.info("No environment files found")
            return {}

def load_env_config():
    """向后兼容的配置加载函数"""
    config_loader = ConfigLoader()
    return config_loader.load_config()