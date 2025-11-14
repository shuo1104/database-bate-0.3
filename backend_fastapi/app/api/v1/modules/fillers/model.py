# -*- coding: utf-8 -*-
"""
填料管理模型
"""

from typing import Optional, List
from sqlalchemy import String, Integer, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FillerTypeModel(Base):
    """填料类型配置表"""
    __tablename__ = "tbl_Config_FillerTypes"
    __table_args__ = {'comment': '无机填料类型配置表'}
    
    FillerTypeID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="填料类型ID"
    )
    
    FillerTypeName: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="填料类型名称"
    )
    
    # 关系
    fillers: Mapped[List["FillerModel"]] = relationship(
        back_populates="filler_type",
        cascade="all, delete-orphan"
    )


class FillerModel(Base):
    """无机填料信息表"""
    __tablename__ = "tbl_InorganicFillers"
    __table_args__ = {'comment': '无机填料信息主表'}
    
    FillerID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="填料ID"
    )
    
    TradeName: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="商品名称"
    )
    
    FillerType_FK: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('tbl_Config_FillerTypes.FillerTypeID', ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="填料类型外键"
    )
    
    Supplier: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="供应商"
    )
    
    ParticleSize: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="粒径（含D50）"
    )
    
    IsSilanized: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        comment="是否硅烷化 (1:是, 0:否)"
    )
    
    CouplingAgent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="所用偶联剂"
    )
    
    SurfaceArea: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4),
        nullable=True,
        comment="比表面积 (m²/g)"
    )
    
    # 关系
    filler_type: Mapped[Optional["FillerTypeModel"]] = relationship(
        back_populates="fillers"
    )
    
    def __repr__(self) -> str:
        return f"<Filler {self.TradeName}>"

