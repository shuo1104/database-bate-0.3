# -*- coding: utf-8 -*-
"""
原料管理Schema
"""

from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from app.core.base_schema import BaseSchema


# ==================== 原料类别Schema ====================
class MaterialCategoryResponse(BaseSchema):
    """原料类别响应"""
    CategoryID: int = Field(..., description="类别ID", alias="CategoryID")
    CategoryName: str = Field(..., description="类别名称", alias="CategoryName")
    
    class Config:
        populate_by_name = True
        from_attributes = True


# ==================== 原料请求Schema ====================
class MaterialCreateRequest(BaseModel):
    """创建原料请求"""
    trade_name: str = Field(..., min_length=1, max_length=255, description="商品名称")
    category_fk: Optional[int] = Field(None, gt=0, description="类别ID（必须大于0）")
    supplier: Optional[str] = Field(None, min_length=1, max_length=255, description="供应商")
    cas_number: Optional[str] = Field(None, min_length=1, max_length=255, description="CAS号")
    density: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=50,
        decimal_places=4,
        description="密度 (g/cm³)，范围: 0-50"
    )
    viscosity: Optional[Decimal] = Field(
        None, 
        ge=0,
        le=1000000,
        decimal_places=2,
        description="粘度 (mPa·s)，范围: 0-1000000"
    )
    function_description: Optional[str] = Field(None, max_length=2000, description="功能说明")
    
    @field_validator("trade_name")
    @classmethod
    def validate_trade_name(cls, v: str) -> str:
        """验证商品名称不为空"""
        if not v or not v.strip():
            raise ValueError("商品名称不能为空")
        return v.strip()
    
    @field_validator("density")
    @classmethod
    def validate_density(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """验证密度值合理性"""
        if v is not None:
            if v < 0:
                raise ValueError("密度不能为负数")
            if v > 50:
                raise ValueError("密度值过大，请检查输入（通常材料密度在0-50 g/cm³之间）")
        return v
    
    @field_validator("viscosity")
    @classmethod
    def validate_viscosity(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """验证粘度值合理性"""
        if v is not None:
            if v < 0:
                raise ValueError("粘度不能为负数")
            if v > 1000000:
                raise ValueError("粘度值过大，请检查输入单位")
        return v


class MaterialUpdateRequest(BaseModel):
    """更新原料请求"""
    trade_name: Optional[str] = Field(None, min_length=1, max_length=255, description="商品名称")
    category_fk: Optional[int] = Field(None, gt=0, description="类别ID（必须大于0）")
    supplier: Optional[str] = Field(None, min_length=1, max_length=255, description="供应商")
    cas_number: Optional[str] = Field(None, min_length=1, max_length=255, description="CAS号")
    density: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=50,
        decimal_places=4,
        description="密度 (g/cm³)，范围: 0-50"
    )
    viscosity: Optional[Decimal] = Field(
        None, 
        ge=0,
        le=1000000,
        decimal_places=2,
        description="粘度 (mPa·s)，范围: 0-1000000"
    )
    function_description: Optional[str] = Field(None, max_length=2000, description="功能说明")
    
    @field_validator("density", "viscosity")
    @classmethod
    def validate_numeric_fields(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """验证数值字段"""
        if v is not None and v < 0:
            raise ValueError(f"{info.field_name} 不能为负数")
        return v


class MaterialQueryParams(BaseModel):
    """原料查询参数"""
    category: Optional[str] = Field(None, description="类别")
    supplier: Optional[str] = Field(None, description="供应商")
    keyword: Optional[str] = Field(None, description="关键词（商品名称或CAS号）")


# ==================== 原料响应Schema ====================
class MaterialResponse(BaseSchema):
    """原料响应"""
    MaterialID: int = Field(..., description="原料ID", alias="MaterialID")
    TradeName: str = Field(..., description="商品名称", alias="TradeName")
    Category_FK: Optional[int] = Field(None, description="类别ID", alias="Category_FK")
    CategoryName: Optional[str] = Field(None, description="类别名称", alias="CategoryName")
    Supplier: Optional[str] = Field(None, description="供应商", alias="Supplier")
    CAS_Number: Optional[str] = Field(None, description="CAS号", alias="CAS_Number")
    Density: Optional[Decimal] = Field(None, description="密度", alias="Density")
    Viscosity: Optional[Decimal] = Field(None, description="粘度", alias="Viscosity")
    FunctionDescription: Optional[str] = Field(None, description="功能说明", alias="FunctionDescription")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: list[int] = Field(..., min_length=1, description="要删除的ID列表")

