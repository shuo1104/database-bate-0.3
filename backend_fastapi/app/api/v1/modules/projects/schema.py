# -*- coding: utf-8 -*-
"""
项目管理Schema
数据验证和序列化模型
"""

from datetime import date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from app.core.base_schema import BaseSchema, TimestampSchema


# ==================== 项目类型Schema ====================
class ProjectTypeResponse(BaseSchema):
    """项目类型响应"""
    TypeID: int = Field(..., description="类型ID", alias="TypeID")
    TypeName: str = Field(..., description="类型名称", alias="TypeName")
    TypeCode: str = Field(..., description="类型代码", alias="TypeCode")
    
    class Config:
        populate_by_name = True
        from_attributes = True


# ==================== 项目请求Schema ====================
class ProjectCreateRequest(BaseModel):
    """创建项目请求"""
    project_name: str = Field(..., max_length=255, description="项目名称")
    project_type_fk: int = Field(..., gt=0, description="项目类型ID")
    substrate_application: Optional[str] = Field(None, description="目标基材或应用领域")
    formulator_name: str = Field(..., max_length=255, description="配方设计师")
    formulation_date: date = Field(..., description="配方设计日期")
    
    @field_validator("project_name", "formulator_name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """验证非空字符串"""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class ProjectUpdateRequest(BaseModel):
    """更新项目请求"""
    project_name: Optional[str] = Field(None, max_length=255, description="项目名称")
    project_type_fk: Optional[int] = Field(None, gt=0, description="项目类型ID")
    substrate_application: Optional[str] = Field(None, description="目标基材或应用领域")
    formulator_name: Optional[str] = Field(None, max_length=255, description="配方设计师")
    formulation_date: Optional[date] = Field(None, description="配方设计日期")


class ProjectQueryParams(BaseModel):
    """项目查询参数"""
    project_type: Optional[str] = Field(None, description="项目类型")
    formulator: Optional[str] = Field(None, description="配方设计师")
    date_start: Optional[date] = Field(None, description="开始日期")
    date_end: Optional[date] = Field(None, description="结束日期")
    keyword: Optional[str] = Field(None, description="关键词（项目名称或配方编码）")
    has_compositions: Optional[bool] = Field(None, description="是否有配方成分")
    has_test_results: Optional[bool] = Field(None, description="是否有测试结果")


# ==================== 项目响应Schema ====================
class ProjectBasicResponse(BaseSchema):
    """项目基本信息响应"""
    ProjectID: int = Field(..., description="项目ID", alias="ProjectID")
    ProjectName: str = Field(..., description="项目名称", alias="ProjectName")
    ProjectType_FK: Optional[int] = Field(None, description="项目类型ID", alias="ProjectType_FK")
    TypeName: Optional[str] = Field(None, description="项目类型名称", alias="TypeName")
    SubstrateApplication: Optional[str] = Field(None, description="目标基材", alias="SubstrateApplication")
    FormulatorName: Optional[str] = Field(None, description="配方设计师", alias="FormulatorName")
    FormulationDate: Optional[date] = Field(None, description="配方设计日期", alias="FormulationDate")
    FormulaCode: Optional[str] = Field(None, description="配方编码", alias="FormulaCode")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class ProjectDetailResponse(ProjectBasicResponse):
    """项目详细信息响应（包含配方成分）"""
    compositions: List["CompositionResponse"] = Field(default=[], description="配方成分列表")


# ==================== 配方成分Schema ====================
class CompositionCreateRequest(BaseModel):
    """创建配方成分请求"""
    project_id: int = Field(..., gt=0, description="项目ID")
    material_id: Optional[int] = Field(None, gt=0, description="原料ID（必须大于0）")
    filler_id: Optional[int] = Field(None, gt=0, description="填料ID（必须大于0）")
    weight_percentage: Decimal = Field(
        ..., 
        ge=0, 
        le=100, 
        decimal_places=4,
        description="重量百分比(%)，范围: 0-100"
    )
    addition_method: Optional[str] = Field(None, max_length=500, description="掺入方法")
    remarks: Optional[str] = Field(None, max_length=1000, description="备注")
    
    @field_validator("weight_percentage")
    @classmethod
    def validate_percentage(cls, v: Decimal) -> Decimal:
        """
        验证重量百分比
        - 必须在 0-100 之间
        - 最多4位小数
        """
        if v < 0:
            raise ValueError("重量百分比不能为负数")
        if v > 100:
            raise ValueError("重量百分比不能超过100%")
        
        # 检查小数位数
        if v.as_tuple().exponent < -4:
            raise ValueError("重量百分比最多支持4位小数")
        
        return v
    
    @field_validator("material_id")
    @classmethod
    def validate_material_id(cls, v: Optional[int]) -> Optional[int]:
        """验证原料ID"""
        if v is not None and v <= 0:
            raise ValueError("原料ID必须大于0")
        return v
    
    @field_validator("filler_id")
    @classmethod
    def validate_filler_id(cls, v: Optional[int]) -> Optional[int]:
        """验证填料ID"""
        if v is not None and v <= 0:
            raise ValueError("填料ID必须大于0")
        return v


class CompositionUpdateRequest(BaseModel):
    """更新配方成分请求"""
    material_id: Optional[int] = Field(None, gt=0, description="原料ID（必须大于0）")
    filler_id: Optional[int] = Field(None, gt=0, description="填料ID（必须大于0）")
    weight_percentage: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=100,
        decimal_places=4,
        description="重量百分比(%)，范围: 0-100"
    )
    addition_method: Optional[str] = Field(None, max_length=500, description="掺入方法")
    remarks: Optional[str] = Field(None, max_length=1000, description="备注")
    
    @field_validator("weight_percentage")
    @classmethod
    def validate_percentage(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """验证重量百分比"""
        if v is None:
            return v
        if v < 0:
            raise ValueError("重量百分比不能为负数")
        if v > 100:
            raise ValueError("重量百分比不能超过100%")
        if v.as_tuple().exponent < -4:
            raise ValueError("重量百分比最多支持4位小数")
        return v


class CompositionResponse(BaseSchema):
    """配方成分响应"""
    CompositionID: int = Field(..., description="成分ID", alias="CompositionID")
    ProjectID_FK: int = Field(..., description="项目ID", alias="ProjectID_FK")
    MaterialID_FK: Optional[int] = Field(None, description="原料ID", alias="MaterialID_FK")
    FillerID_FK: Optional[int] = Field(None, description="填料ID", alias="FillerID_FK")
    WeightPercentage: Decimal = Field(..., description="重量百分比", alias="WeightPercentage")
    AdditionMethod: Optional[str] = Field(None, description="掺入方法", alias="AdditionMethod")
    Remarks: Optional[str] = Field(None, description="备注", alias="Remarks")
    MaterialName: Optional[str] = Field(None, description="原料名称", alias="MaterialName")
    FillerName: Optional[str] = Field(None, description="填料名称", alias="FillerName")
    
    class Config:
        populate_by_name = True
        from_attributes = True


# ==================== 测试结果Schema ====================
class TestResultInkRequest(BaseModel):
    """喷墨测试结果请求"""
    project_id: int = Field(..., gt=0, description="项目ID")
    ink_viscosity: Optional[str] = Field(None, max_length=255, description="粘度")
    ink_reactivity: Optional[str] = Field(None, max_length=255, description="反应活性/固化时间")
    ink_particle_size: Optional[str] = Field(None, max_length=255, description="粒径(nm)")
    ink_surface_tension: Optional[str] = Field(None, max_length=255, description="表面张力(mN/m)")
    ink_color_value: Optional[str] = Field(None, max_length=255, description="色度(Lab*色值)")
    ink_rheology_note: Optional[str] = Field(None, description="流变学说明")
    test_date: Optional[date] = Field(None, description="测试日期")
    notes: Optional[str] = Field(None, description="备注")


class TestResultInkResponse(BaseSchema):
    """喷墨测试结果响应"""
    ResultID: int = Field(..., description="结果ID", alias="ResultID")
    ProjectID_FK: int = Field(..., description="项目ID", alias="ProjectID_FK")
    Ink_Viscosity: Optional[str] = Field(None, description="粘度", alias="Ink_Viscosity")
    Ink_Reactivity: Optional[str] = Field(None, description="反应活性", alias="Ink_Reactivity")
    Ink_ParticleSize: Optional[str] = Field(None, description="粒径", alias="Ink_ParticleSize")
    Ink_SurfaceTension: Optional[str] = Field(None, description="表面张力", alias="Ink_SurfaceTension")
    Ink_ColorValue: Optional[str] = Field(None, description="色度", alias="Ink_ColorValue")
    Ink_RheologyNote: Optional[str] = Field(None, description="流变学说明", alias="Ink_RheologyNote")
    TestDate: Optional[date] = Field(None, description="测试日期", alias="TestDate")
    Notes: Optional[str] = Field(None, description="备注", alias="Notes")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class TestResultCoatingRequest(BaseModel):
    """涂层测试结果请求"""
    project_id: int = Field(..., gt=0, description="项目ID")
    coating_adhesion: Optional[str] = Field(None, max_length=255, description="附着力")
    coating_transparency: Optional[str] = Field(None, max_length=255, description="透明度")
    coating_surface_hardness: Optional[str] = Field(None, max_length=255, description="表面硬度")
    coating_chemical_resistance: Optional[str] = Field(None, max_length=255, description="耐化学性")
    coating_cost_estimate: Optional[str] = Field(None, max_length=255, description="成本估算")
    test_date: Optional[date] = Field(None, description="测试日期")
    notes: Optional[str] = Field(None, description="备注")


class TestResultCoatingResponse(BaseSchema):
    """涂层测试结果响应"""
    ResultID: int = Field(..., description="结果ID", alias="ResultID")
    ProjectID_FK: int = Field(..., description="项目ID", alias="ProjectID_FK")
    Coating_Adhesion: Optional[str] = Field(None, description="附着力", alias="Coating_Adhesion")
    Coating_Transparency: Optional[str] = Field(None, description="透明度", alias="Coating_Transparency")
    Coating_SurfaceHardness: Optional[str] = Field(None, description="表面硬度", alias="Coating_SurfaceHardness")
    Coating_ChemicalResistance: Optional[str] = Field(None, description="耐化学性", alias="Coating_ChemicalResistance")
    Coating_CostEstimate: Optional[str] = Field(None, description="成本估算", alias="Coating_CostEstimate")
    TestDate: Optional[date] = Field(None, description="测试日期", alias="TestDate")
    Notes: Optional[str] = Field(None, description="备注", alias="Notes")
    
    class Config:
        populate_by_name = True
        from_attributes = True


# ==================== 批量操作Schema ====================
class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., min_length=1, description="要删除的ID列表")

