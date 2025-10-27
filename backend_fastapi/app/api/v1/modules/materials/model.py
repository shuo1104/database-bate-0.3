# -*- coding: utf-8 -*-
"""
原料管理模型
"""

from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MaterialCategoryModel(Base):
    """原料类别配置表"""
    __tablename__ = "tbl_Config_MaterialCategories"
    __table_args__ = {'comment': '原料类别配置表'}
    
    CategoryID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="类别ID"
    )
    
    CategoryName: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="类别名称"
    )
    
    # 关系
    materials: Mapped[list["MaterialModel"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan"
    )


class MaterialModel(Base):
    """原料信息主表"""
    __tablename__ = "tbl_RawMaterials"
    __table_args__ = {'comment': '原料信息主表'}
    
    MaterialID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="原料ID"
    )
    
    TradeName: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="商品名称"
    )
    
    Category_FK: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('tbl_Config_MaterialCategories.CategoryID', ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="类别外键"
    )
    
    Supplier: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="供应商"
    )
    
    CAS_Number: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="化学文摘登记号"
    )
    
    Density: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4),
        nullable=True,
        comment="密度"
    )
    
    Viscosity: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4),
        nullable=True,
        comment="粘度"
    )
    
    FunctionDescription: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="功能说明"
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
    category: Mapped[Optional["MaterialCategoryModel"]] = relationship(
        back_populates="materials",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Material {self.TradeName}>"

