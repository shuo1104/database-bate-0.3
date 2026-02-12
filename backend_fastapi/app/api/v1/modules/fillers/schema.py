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
    trade_name: str = Field(..., min_length=1, max_length=255, description="商品名称")
    filler_type_fk: Optional[int] = Field(None, gt=0, description="填料类型ID（必须大于0）")
    supplier: Optional[str] = Field(None, min_length=1, max_length=255, description="供应商")
    particle_size: Optional[str] = Field(None, min_length=1, max_length=255, description="粒径")
    is_silanized: Optional[int] = Field(None, ge=0, le=1, description="是否硅烷化 (1:是, 0:否)")
    coupling_agent: Optional[str] = Field(None, min_length=1, max_length=255, description="所用偶联剂")
    surface_area: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=10000,
        decimal_places=2,
        description="比表面积 (m²/g)，范围: 0-10000"
    )
    
    @field_validator("trade_name")
    @classmethod
    def validate_trade_name(cls, v: str) -> str:
        """验证商品名称不为空"""
        if not v or not v.strip():
            raise ValueError("商品名称不能为空")
        return v.strip()
    
    @field_validator("is_silanized")
    @classmethod
    def validate_is_silanized(cls, v: Optional[int]) -> Optional[int]:
        """验证硅烷化标志"""
        if v is not None and v not in [0, 1]:
            raise ValueError("是否硅烷化只能为 0（否）或 1（是）")
        return v
    
    @field_validator("surface_area")
    @classmethod
    def validate_surface_area(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """验证比表面积"""
        if v is not None:
            if v < 0:
                raise ValueError("比表面积不能为负数")
            if v > 10000:
                raise ValueError("比表面积值过大，请检查输入（通常在0-10000 m²/g之间）")
        return v


class FillerUpdateRequest(BaseModel):
    """更新填料请求"""
    trade_name: Optional[str] = Field(None, min_length=1, max_length=255, description="商品名称")
    filler_type_fk: Optional[int] = Field(None, gt=0, description="填料类型ID（必须大于0）")
    supplier: Optional[str] = Field(None, min_length=1, max_length=255, description="供应商")
    particle_size: Optional[str] = Field(None, min_length=1, max_length=255, description="粒径")
    is_silanized: Optional[int] = Field(None, ge=0, le=1, description="是否硅烷化 (1:是, 0:否)")
    coupling_agent: Optional[str] = Field(None, min_length=1, max_length=255, description="所用偶联剂")
    surface_area: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=10000,
        decimal_places=2,
        description="比表面积 (m²/g)，范围: 0-10000"
    )
    
    @field_validator("is_silanized")
    @classmethod
    def validate_is_silanized(cls, v: Optional[int]) -> Optional[int]:
        """验证硅烷化标志"""
        if v is not None and v not in [0, 1]:
            raise ValueError("是否硅烷化只能为 0（否）或 1（是）")
        return v
    
    @field_validator("surface_area")
    @classmethod
    def validate_surface_area(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """验证比表面积"""
        if v is not None and v < 0:
            raise ValueError("比表面积不能为负数")
        return v


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

