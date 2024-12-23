from fastapi import APIRouter
from api.v1.endpoints import assets

api_router = APIRouter()

# 包含资产相关的路由
api_router.include_router(
    assets.router,
    prefix="/assets",
    tags=["assets"]
)