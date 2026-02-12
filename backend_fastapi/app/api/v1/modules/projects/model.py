# -*- coding: utf-8 -*-
"""
项目管理模型
包含项目信息、配方成分、测试结果等表
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    String, Integer, DateTime, Date, Text, ForeignKey, 
    Numeric, Boolean, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ==================== 配置表 ====================
class ProjectTypeModel(Base):
    """项目类型配置表"""
    __tablename__ = "tbl_Config_ProjectTypes"
    __table_args__ = {'comment': '项目类型配置表'}
    
    TypeID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="类型ID"
    )
    
    TypeName: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="类型名称（如：喷墨、涂层、3D打印、复合材料）"
    )
    
    TypeCode: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        unique=True,
        comment="类型代码（用于配方编码）"
    )
    
    # 关系
    projects: Mapped[List["ProjectModel"]] = relationship(
        back_populates="project_type",
        cascade="all, delete-orphan"
    )


# ==================== 项目信息表 ====================
class ProjectModel(Base):
    """项目基本信息表"""
    __tablename__ = "tbl_ProjectInfo"
    __table_args__ = {'comment': '项目基本信息表'}
    
    ProjectID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="项目ID"
    )
    
    ProjectName: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="项目名称"
    )
    
    ProjectType_FK: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('tbl_Config_ProjectTypes.TypeID', ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="项目类型外键"
    )
    
    SubstrateApplication: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="目标基材或应用领域"
    )
    
    FormulatorName: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="配方设计师姓名"
    )
    
    FormulationDate: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="配方设计日期"
    )
    
    FormulaCode: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        comment="配方编码（自动生成）"
    )
    
    # ReservedField1: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段1"
    # )
    
    # ReservedField2: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段2"
    # )
    
    # 关系
    project_type: Mapped[Optional["ProjectTypeModel"]] = relationship(
        back_populates="projects",
        lazy="selectin"
    )
    
    compositions: Mapped[List["FormulaCompositionModel"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Project {self.ProjectName} ({self.FormulaCode})>"


# ==================== 配方成分表 ====================
class FormulaCompositionModel(Base):
    """配方成分表"""
    __tablename__ = "tbl_FormulaComposition"
    __table_args__ = {'comment': '配方成分表'}
    
    CompositionID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="成分ID"
    )
    
    ProjectID_FK: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('tbl_ProjectInfo.ProjectID', ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="项目ID外键"
    )
    
    MaterialID_FK: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('tbl_RawMaterials.MaterialID', ondelete="SET NULL"),
        nullable=True,
        comment="原料ID外键"
    )
    
    FillerID_FK: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('tbl_InorganicFillers.FillerID', ondelete="SET NULL"),
        nullable=True,
        comment="填料ID外键"
    )
    
    WeightPercentage: Mapped[float] = mapped_column(
        Numeric(7, 4),
        nullable=False,
        comment="重量百分比(%)"
    )
    
    AdditionMethod: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="掺入方法"
    )
    
    Remarks: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # ReservedField1: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段1"
    # )
    
    # ReservedField2: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段2"
    # )
    
    # 关系
    project: Mapped["ProjectModel"] = relationship(
        back_populates="compositions"
    )
    
    material: Mapped[Optional["MaterialModel"]] = relationship(
        foreign_keys=[MaterialID_FK]
    )
    
    filler: Mapped[Optional["FillerModel"]] = relationship(
        foreign_keys=[FillerID_FK]
    )
    
    def __repr__(self) -> str:
        return f"<Composition {self.CompositionID} - {self.WeightPercentage}%>"


# ==================== 测试结果表 - 喷墨 ====================
class TestResultInkModel(Base):
    """测试结果表 - 喷墨"""
    __tablename__ = "tbl_TestResults_Ink"
    __table_args__ = {'comment': '测试结果数据表-喷墨'}
    
    ResultID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="结果ID"
    )
    
    ProjectID_FK: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('tbl_ProjectInfo.ProjectID', ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="项目ID外键"
    )
    
    Ink_Viscosity: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="粘度"
    )
    
    Ink_Reactivity: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="反应活性/固化时间"
    )
    
    Ink_ParticleSize: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="粒径(nm)"
    )
    
    Ink_SurfaceTension: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="表面张力(mN/m)"
    )
    
    Ink_ColorValue: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="色度(Lab*色值)"
    )
    
    Ink_RheologyNote: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="流变学说明或文件"
    )
    
    TestDate: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="测试日期"
    )
    
    Notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # ReservedField1: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段1"
    # )
    
    # ReservedField2: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段2"
    # )


# ==================== 测试结果表 - 涂层 ====================
class TestResultCoatingModel(Base):
    """测试结果表 - 涂层"""
    __tablename__ = "tbl_TestResults_Coating"
    __table_args__ = {'comment': '测试结果数据表-涂层'}
    
    ResultID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="结果ID"
    )
    
    ProjectID_FK: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('tbl_ProjectInfo.ProjectID', ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="项目ID外键"
    )
    
    Coating_Adhesion: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="附着力"
    )
    
    Coating_Transparency: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="透明度"
    )
    
    Coating_SurfaceHardness: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="表面硬度"
    )
    
    Coating_ChemicalResistance: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="耐化学性"
    )
    
    Coating_CostEstimate: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="成本估算(€/kg)"
    )
    
    TestDate: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="测试日期"
    )
    
    Notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # ReservedField1: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段1"
    # )
    
    # ReservedField2: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段2"
    # )


# ==================== 测试结果表 - 3D打印 ====================
class TestResult3DPrintModel(Base):
    """测试结果表 - 3D打印"""
    __tablename__ = "tbl_TestResults_3DPrint"
    __table_args__ = {'comment': '测试结果数据表-3D打印'}
    
    ResultID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="结果ID"
    )
    
    ProjectID_FK: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('tbl_ProjectInfo.ProjectID', ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="项目ID外键"
    )
    
    Print3D_Shrinkage: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="收缩率(%)"
    )
    
    Print3D_YoungsModulus: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="杨氏模量"
    )
    
    Print3D_FlexuralStrength: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="弯曲强度"
    )
    
    Print3D_ShoreHardness: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="邵氏硬度"
    )
    
    Print3D_ImpactResistance: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="抗冲击性"
    )
    
    TestDate: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="测试日期"
    )
    
    Notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # ReservedField1: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段1"
    # )
    
    # ReservedField2: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段2"
    # )


# ==================== 测试结果表 - 复合材料 ====================
class TestResultCompositeModel(Base):
    """测试结果表 - 复合材料"""
    __tablename__ = "tbl_TestResults_Composite"
    __table_args__ = {'comment': '测试结果数据表-复合材料'}
    
    ResultID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="结果ID"
    )
    
    ProjectID_FK: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('tbl_ProjectInfo.ProjectID', ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="项目ID外键"
    )
    
    Composite_FlexuralStrength: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="弯曲强度"
    )
    
    Composite_YoungsModulus: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="杨氏模量"
    )
    
    Composite_ImpactResistance: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="抗冲击性"
    )
    
    Composite_ConversionRate: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="转化率(可选)"
    )
    
    Composite_WaterAbsorption: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="吸水率/溶解度(可选)"
    )
    
    TestDate: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="测试日期"
    )
    
    Notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # ReservedField1: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段1"
    # )
    
    # ReservedField2: Mapped[Optional[str]] = mapped_column(
    #     Text,
    #     nullable=True,
    #     comment="备用字段2"
    # )

