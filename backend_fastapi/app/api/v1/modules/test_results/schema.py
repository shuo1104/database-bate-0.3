# -*- coding: utf-8 -*-
"""
测试结果管理Schema
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

from app.core.base_schema import BaseSchema


# ==================== 测试结果请求Schema ====================

class TestResultInkRequest(BaseModel):
    """喷墨测试结果请求"""
    Ink_Viscosity: Optional[str] = Field(None, description="粘度")
    Ink_Reactivity: Optional[str] = Field(None, description="反应活性/固化时间")
    Ink_ParticleSize: Optional[str] = Field(None, description="粒径(nm)")
    Ink_SurfaceTension: Optional[str] = Field(None, description="表面张力(mN/m)")
    Ink_ColorValue: Optional[str] = Field(None, description="色度(Lab*色值)")
    Ink_RheologyNote: Optional[str] = Field(None, description="流变学说明或文件")
    TestDate: Optional[date] = Field(None, description="测试日期")
    Notes: Optional[str] = Field(None, description="备注")


class TestResultCoatingRequest(BaseModel):
    """涂层测试结果请求"""
    Coating_Adhesion: Optional[str] = Field(None, description="附着力")
    Coating_Transparency: Optional[str] = Field(None, description="透明度")
    Coating_SurfaceHardness: Optional[str] = Field(None, description="表面硬度")
    Coating_ChemicalResistance: Optional[str] = Field(None, description="耐化学性")
    Coating_CostEstimate: Optional[str] = Field(None, description="成本估算(€/kg)")
    TestDate: Optional[date] = Field(None, description="测试日期")
    Notes: Optional[str] = Field(None, description="备注")


class TestResult3DPrintRequest(BaseModel):
    """3D打印测试结果请求"""
    Print3D_Shrinkage: Optional[str] = Field(None, description="收缩率(%)")
    Print3D_YoungsModulus: Optional[str] = Field(None, description="杨氏模量")
    Print3D_FlexuralStrength: Optional[str] = Field(None, description="弯曲强度")
    Print3D_ShoreHardness: Optional[str] = Field(None, description="邵氏硬度")
    Print3D_ImpactResistance: Optional[str] = Field(None, description="抗冲击性")
    TestDate: Optional[date] = Field(None, description="测试日期")
    Notes: Optional[str] = Field(None, description="备注")


class TestResultCompositeRequest(BaseModel):
    """复合材料测试结果请求"""
    Composite_FlexuralStrength: Optional[str] = Field(None, description="弯曲强度")
    Composite_YoungsModulus: Optional[str] = Field(None, description="杨氏模量")
    Composite_ImpactResistance: Optional[str] = Field(None, description="抗冲击性")
    Composite_ConversionRate: Optional[str] = Field(None, description="转化率(可选)")
    Composite_WaterAbsorption: Optional[str] = Field(None, description="吸水率/溶解度(可选)")
    TestDate: Optional[date] = Field(None, description="测试日期")
    Notes: Optional[str] = Field(None, description="备注")


# ==================== 测试结果响应Schema ====================

class TestResultInkResponse(BaseSchema):
    """喷墨测试结果响应"""
    ResultID: int = Field(..., description="结果ID", alias="ResultID")
    ProjectID_FK: int = Field(..., description="项目ID", alias="ProjectID_FK")
    Ink_Viscosity: Optional[str] = Field(None, alias="Ink_Viscosity")
    Ink_Reactivity: Optional[str] = Field(None, alias="Ink_Reactivity")
    Ink_ParticleSize: Optional[str] = Field(None, alias="Ink_ParticleSize")
    Ink_SurfaceTension: Optional[str] = Field(None, alias="Ink_SurfaceTension")
    Ink_ColorValue: Optional[str] = Field(None, alias="Ink_ColorValue")
    Ink_RheologyNote: Optional[str] = Field(None, alias="Ink_RheologyNote")
    TestDate: Optional[date] = Field(None, alias="TestDate")
    Notes: Optional[str] = Field(None, alias="Notes")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class TestResultCoatingResponse(BaseSchema):
    """涂层测试结果响应"""
    ResultID: int = Field(..., description="结果ID", alias="ResultID")
    ProjectID_FK: int = Field(..., description="项目ID", alias="ProjectID_FK")
    Coating_Adhesion: Optional[str] = Field(None, alias="Coating_Adhesion")
    Coating_Transparency: Optional[str] = Field(None, alias="Coating_Transparency")
    Coating_SurfaceHardness: Optional[str] = Field(None, alias="Coating_SurfaceHardness")
    Coating_ChemicalResistance: Optional[str] = Field(None, alias="Coating_ChemicalResistance")
    Coating_CostEstimate: Optional[str] = Field(None, alias="Coating_CostEstimate")
    TestDate: Optional[date] = Field(None, alias="TestDate")
    Notes: Optional[str] = Field(None, alias="Notes")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class TestResult3DPrintResponse(BaseSchema):
    """3D打印测试结果响应"""
    ResultID: int = Field(..., description="结果ID", alias="ResultID")
    ProjectID_FK: int = Field(..., description="项目ID", alias="ProjectID_FK")
    Print3D_Shrinkage: Optional[str] = Field(None, alias="Print3D_Shrinkage")
    Print3D_YoungsModulus: Optional[str] = Field(None, alias="Print3D_YoungsModulus")
    Print3D_FlexuralStrength: Optional[str] = Field(None, alias="Print3D_FlexuralStrength")
    Print3D_ShoreHardness: Optional[str] = Field(None, alias="Print3D_ShoreHardness")
    Print3D_ImpactResistance: Optional[str] = Field(None, alias="Print3D_ImpactResistance")
    TestDate: Optional[date] = Field(None, alias="TestDate")
    Notes: Optional[str] = Field(None, alias="Notes")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class TestResultCompositeResponse(BaseSchema):
    """复合材料测试结果响应"""
    ResultID: int = Field(..., description="结果ID", alias="ResultID")
    ProjectID_FK: int = Field(..., description="项目ID", alias="ProjectID_FK")
    Composite_FlexuralStrength: Optional[str] = Field(None, alias="Composite_FlexuralStrength")
    Composite_YoungsModulus: Optional[str] = Field(None, alias="Composite_YoungsModulus")
    Composite_ImpactResistance: Optional[str] = Field(None, alias="Composite_ImpactResistance")
    Composite_ConversionRate: Optional[str] = Field(None, alias="Composite_ConversionRate")
    Composite_WaterAbsorption: Optional[str] = Field(None, alias="Composite_WaterAbsorption")
    TestDate: Optional[date] = Field(None, alias="TestDate")
    Notes: Optional[str] = Field(None, alias="Notes")
    
    class Config:
        populate_by_name = True
        from_attributes = True

