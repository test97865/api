from pydantic import BaseModel, Field
from typing import Optional

class AssetsCreate(BaseModel):
    identifier: str
    url: str
    timestamp: str
    search_engine: str
    query_statements: str
    protocol: Optional[str] = None
    ip: str
    port: Optional[int] = None
    domain: Optional[str] = None
    title: Optional[str] = None
    product: Optional[str] = None
    product_category: Optional[str] = None
    country: Optional[str] = None
    country_name: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    os: Optional[str] = None
    as_organization: Optional[str] = None
    lastupdatetime: Optional[str] = None
    icp: Optional[str] = None

class AssetsResponse(AssetsCreate):
    id: int

    class Config:
        from_attributes = True

class AssetsFilter(BaseModel):
    id: Optional[str] = Field(None, alias='identifier')
    ip: Optional[str] = None
    port: Optional[int] = None
    domain: Optional[str] = None
    title: Optional[str] = None
    product: Optional[str] = None
    country: Optional[str] = None
    s: Optional[str] = Field(None, alias='search_engine')
    protocol: Optional[str] = None
    org: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True  # 添加这个配置