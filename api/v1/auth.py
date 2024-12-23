from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from typing import Optional
from config.auth import auth_settings
import logging
import os

# 设置日志
logger = logging.getLogger(__name__)

# 使用小写的 apikey
api_key_header = APIKeyHeader(name="apikey", auto_error=False)

def get_client_ip(request: Request) -> str:
    """获取客户端真实IP"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host

async def verify_api_key(
    request: Request,
    api_key: Optional[str] = Security(api_key_header)
) -> bool:
    """为了保持向后兼容的API key验证函数"""
    return await verify_access(request, api_key)

async def verify_access(
    request: Request,
    api_key: Optional[str] = Security(api_key_header)
) -> bool:
    """验证访问权限"""
    # 获取环境
    env = os.getenv('ENV', 'local')
    client_ip = get_client_ip(request)
    
    # 本地环境不需要验证
    if env != 'prod':
        logger.info(f"本地环境，跳过验证: {client_ip}")
        return True
    
    # 生产环境下验证API key
    if not api_key:
        logger.error(f"生产环境需要API key: {client_ip}")
        raise HTTPException(
            status_code=401,
            detail="API key required in production environment"
        )
    
    valid_keys = auth_settings.get_api_keys()
    api_key = api_key.strip()
    valid_keys = [k.strip() for k in valid_keys]
    
    if api_key not in valid_keys:
        logger.error(f"无效的API key: {api_key}, IP: {client_ip}")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    logger.info(f"API key验证成功: {client_ip}")
    return True