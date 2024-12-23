from typing import List, Optional, Dict, Any
from database.connection import get_db
from schemas.assets import AssetsCreate, AssetsFilter
from datetime import datetime
import logging
from cachetools import TTLCache
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class AssetsService:
    _cache = TTLCache(maxsize=10000, ttl=300)  # 5分钟过期

    @staticmethod
    def _parse_datetime(date_str: str) -> datetime:
        """解析时间字符串，支持多种格式"""
        formats = [
            "%Y%m%d",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M",
            "%Y%m%d%H%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y%m%d%H%M%S"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"无法解析时间格式: {date_str}，支持的格式有：YYYYMMDD, YYYY-MM-DD, YYYY-MM-DD HH:MM, YYYYMMDDHHMM")

    @staticmethod
    async def create_asset(asset: AssetsCreate) -> Dict[str, Any]:
        """创建资产记录"""
        db = get_db()
        conn = db.get_connection()
        
        try:
            if hasattr(conn, 'table'):  # Supabase
                result = conn.table('assets').insert(asset.model_dump()).execute()
                return result.data[0] if result.data else None
            else:  # MySQL
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    """
                    INSERT INTO assets (
                        identifier, url, timestamp, search_engine, query_statements,
                        protocol, ip, port, domain, title, product, product_category,
                        country, country_name, region, city, os, as_organization,
                        lastupdatetime, icp
                    ) VALUES (
                        %(identifier)s, %(url)s, %(timestamp)s, %(search_engine)s,
                        %(query_statements)s, %(protocol)s, %(ip)s, %(port)s,
                        %(domain)s, %(title)s, %(product)s, %(product_category)s,
                        %(country)s, %(country_name)s, %(region)s, %(city)s,
                        %(os)s, %(as_organization)s, %(lastupdatetime)s, %(icp)s
                    )
                    """,
                    asset.model_dump()
                )
                conn.commit()
                return {**asset.model_dump(), "id": cursor.lastrowid}
        except Exception as e:
            logger.error(f"创建资产失败: {str(e)}")
            raise

    @staticmethod
    async def get_assets(
        skip: int = 0,
        limit: int = 10,
        filters: Optional[AssetsFilter] = None
    ) -> List[Dict[str, Any]]:
        """获取资产列表"""
        db = get_db()
        conn = db.get_connection()
        
        try:
            logger.info(f"当前使用的数据库连接类型: {'Supabase' if hasattr(conn, 'table') else 'MySQL'}")
            if hasattr(conn, 'table'):  # Supabase
                query = conn.table('assets').select('*')
                
                # 添加过滤条件
                if filters:
                    if filters.id:
                        query = query.eq('identifier', filters.id)
                    if filters.ip:
                        query = query.eq('ip', filters.ip)
                    # ... 其他过滤条件 ...
                
                result = query.range(skip, skip + limit - 1).execute()
                return result.data
            else:  # MySQL
                cursor = conn.cursor(dictionary=True)
                where_conditions = []
                params = {}
                
                if filters:
                    if filters.id:
                        where_conditions.append("identifier = %(identifier)s")
                        params['identifier'] = filters.id
                    # ... 其他过滤条件 ...
                
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                
                query = f"""
                    SELECT * FROM assets 
                    WHERE {where_clause}
                    LIMIT %(limit)s OFFSET %(offset)s
                """
                params.update({'limit': limit, 'offset': skip})
                
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"获取资产列表失败: {str(e)}")
            raise

    @staticmethod
    async def get_asset_by_identifier(identifier: str) -> Optional[Dict[str, Any]]:
        """根据标识符获取资产"""
        db = get_db()
        conn = db.get_connection()
        
        try:
            if hasattr(conn, 'table'):  # Supabase
                result = conn.table('assets').select('*').eq('identifier', identifier).execute()
                return result.data[0] if result.data else None
            else:  # MySQL
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM assets WHERE identifier = %s",
                    (identifier,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"获取资产失败: {str(e)}")
            raise

    @staticmethod
    async def delete_assets(
        title: Optional[str] = None,
        search_engine: Optional[str] = None,
        before: Optional[str] = None,
        date_limit: Optional[datetime] = None,
        country_name: Optional[str] = None,
        region: Optional[str] = None
    ) -> int:
        query = Assets.delete()
        conditions = []

        if title:
            conditions.append(Assets.title.contains(title))
        if search_engine:
            conditions.append(Assets.search_engine == search_engine)
        if before:
            before_date = AssetsService._parse_datetime(before)
            conditions.append(Assets.lastupdatetime < before_date)
        if date_limit:
            # 删除超过 date_limit 天的数据
            conditions.append(Assets.lastupdatetime < date_limit)
        if country_name:
            conditions.append(Assets.country_name.contains(country_name))
        if region:
            conditions.append(Assets.region.contains(region))

        for condition in conditions:
            query = query.where(condition)

        deleted_count = query.execute()
        return deleted_count

    @staticmethod
    async def get_assets_with_cache(skip: int, limit: int, filters_hash: str):
        """带缓存的资产获取"""
        cache_key = f"{skip}:{limit}:{filters_hash}"
        if cache_key not in AssetsService._cache:
            AssetsService._cache[cache_key] = await AssetsService.get_assets(skip, limit, filters)
        return AssetsService._cache[cache_key]

    @staticmethod
    async def get_large_dataset(skip: int, limit: int, filters: AssetsFilter):
        """并行处理大量数据"""
        chunk_size = 1000
        chunks = [(i, min(chunk_size, limit - i)) 
                 for i in range(0, limit, chunk_size)]
        
        with ThreadPoolExecutor() as executor:
            results = await asyncio.gather(*[
                AssetsService.get_assets(skip + offset, size, filters)
                for offset, size in chunks
            ])
        
        return [item for chunk in results for item in chunk]

    @staticmethod
    async def get_assets_count(filters: Optional[AssetsFilter] = None) -> int:
        """获取资产总数"""
        db = get_db()
        conn = db.get_connection()
        
        try:
            if hasattr(conn, 'table'):  # Supabase
                query = conn.table('assets').select('*', count='exact')
                
                # 添加过滤条件
                if filters:
                    if filters.id:
                        query = query.eq('identifier', filters.id)
                    if filters.ip:
                        query = query.eq('ip', filters.ip)
                    # ... 其他过滤条件 ...
                
                result = query.execute()
                return result.count
            else:  # MySQL
                cursor = conn.cursor()
                where_conditions = []
                params = {}
                
                if filters:
                    if filters.id:
                        where_conditions.append("identifier = %(identifier)s")
                        params['identifier'] = filters.id
                    # ... 其他过滤条件 ...
                
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                
                query = f"SELECT COUNT(*) FROM assets WHERE {where_clause}"
                cursor.execute(query, params)
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"获取资产总数失败: {str(e)}")
            raise