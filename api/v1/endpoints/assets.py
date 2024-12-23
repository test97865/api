from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict
import logging
import time
from schemas.assets import AssetsCreate, AssetsResponse, AssetsFilter
from services.assets import AssetsService
from datetime import datetime, timedelta
from ..auth import verify_api_key

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=AssetsResponse, dependencies=[Depends(verify_api_key)])
async def create_asset(asset: AssetsCreate):
    """创建新的资产记录"""
    try:
        # 检查记录是否已存在
        existing_asset = await AssetsService.get_asset_by_identifier(asset.identifier)
        if existing_asset:
            raise HTTPException(status_code=400, detail="资产记录已存在")
            
        created_asset = await AssetsService.create_asset(asset)
        return created_asset
    except Exception as e:
        logger.error(f"创建资产失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", dependencies=[Depends(verify_api_key)])
async def get_assets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=10000),
    filters: AssetsFilter = Depends()
):
    """获取资产列表"""
    try:
        total = await AssetsService.get_assets_count(filters)
        items = await AssetsService.get_assets(skip=skip, limit=limit, filters=filters)
        return {
            "total": total,
            "items": items
        }
    except Exception as e:
        logger.error(f"获取资产列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/", dependencies=[Depends(verify_api_key)])
async def delete_assets(
    title: Optional[str] = None,
    search_engine: Optional[str] = None,
    day: Optional[int] = None,
    before: Optional[str] = None,
    country_name: Optional[str] = None,
    region: Optional[str] = None
):
    """通过title, search_engine, day, before, country_name, region参数删除资产"""
    try:
        # 计算day参数的日期限制
        date_limit = None
        if day is not None:
            date_limit = datetime.now() - timedelta(days=day)
        
        deleted_count = await AssetsService.delete_assets(
            title=title,
            search_engine=search_engine,
            before=before,
            date_limit=date_limit,
            country_name=country_name,
            region=region
        )
        return {"deleted_count": deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-connection", dependencies=[Depends(verify_api_key)])
async def test_connection():
    """测试数据库连接"""
    from database.connection import get_db
    try:
        db = get_db()
        conn = db.get_connection()
        if hasattr(conn, 'table'):
            return {"status": "success", "connection": "Supabase"}
        else:
            return {"status": "success", "connection": "MySQL"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))