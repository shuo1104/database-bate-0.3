# -*- coding: utf-8 -*-
"""
填料管理Schema
"""

from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from app.core.base_schema import BaseSchema


# ==================== 填料类型Schema ====================
class FillerTypeResponse(BaseSchema):
    """填料类型响应"""
    FillerTypeID: int = Field(..., description="填料类型ID", alias="FillerTypeID")
    FillerTypeName: str = Field(..., description="填料类型名称", alias="FillerTypeName")
    
    class Config:
        populate_by_name = True
        from_attributes = True


# ==================== 填料请求Schema ====================
class FillerCreateRequest(BaseModel):
    """创建填料请求"""
    trade_name: str = Field(..., max_length=255, description="商品名称")
    filler_type_fk: Optional[int] = Field(None, description="填料类型ID")
    supplier: Optional[str] = Field(None, max_length=255, description="供应商")
    particle_size: Optional[str] = Field(None, max_length=255, description="粒径")
    is_silanized: Optional[int] = Field(None, ge=0, le=1, description="是否硅烷化 (1:是, 0:否)")
    coupling_agent: Optional[str] = Field(None, max_length=255, description="所用偶联剂")
    surface_area: Optional[Decimal] = Field(None, ge=0, description="比表面积 (m²/g)")
    
    @field_validator("trade_name")
    @classmethod
    def validate_trade_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Trade name cannot be empty")
        return v.strip()


class FillerUpdateRequest(BaseModel):
    """更新填料请求"""
    trade_name: Optional[str] = Field(None, max_length=255, description="商品名称")
    filler_type_fk: Optional[int] = Field(None, description="填料类型ID")
    supplier: Optional[str] = Field(None, max_length=255, description="供应商")
    particle_size: Optional[str] = Field(None, max_length=255, description="粒径")
    is_silanized: Optional[int] = Field(None, ge=0, le=1, description="是否硅烷化 (1:是, 0:否)")
    coupling_agent: Optional[str] = Field(None, max_length=255, description="所用偶联剂")
    surface_area: Optional[Decimal] = Field(None, ge=0, description="比表面积 (m²/g)")


class FillerQueryParams(BaseModel):
    """填料查询参数"""
    filler_type: Optional[str] = Field(None, description="填料类型")
    supplier: Optional[str] = Field(None, description="供应商")
    keyword: Optional[str] = Field(None, description="关键词（商品名称）")


# ==================== 填料响应Schema ====================
class FillerResponse(BaseSchema):
    """填料响应"""
    FillerID: int = Field(..., description="填料ID", alias="FillerID")
    TradeName: str = Field(..., description="商品名称", alias="TradeName")
    FillerType_FK: Optional[int] = Field(None, description="填料类型ID", alias="FillerType_FK")
    FillerTypeName: Optional[str] = Field(None, description="填料类型名称", alias="FillerTypeName")
    Supplier: Optional[str] = Field(None, description="供应商", alias="Supplier")
    ParticleSize: Optional[str] = Field(None, description="粒径", alias="ParticleSize")
    IsSilanized: Optional[int] = Field(None, description="是否硅烷化", alias="IsSilanized")
    CouplingAgent: Optional[str] = Field(None, description="所用偶联剂", alias="CouplingAgent")
    SurfaceArea: Optional[Decimal] = Field(None, description="比表面积", alias="SurfaceArea")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: list[int] = Field(..., min_length=1, description="要删除的ID列表")

