# -*- coding: utf-8 -*-
"""
用户认证模型
对应原tbl_Users表
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    admin = "admin"
    user = "user"


class UserModel(Base):
    """
    用户模型
    对应数据库表: tbl_Users
    """
    __tablename__ = "tbl_Users"
    __table_args__ = {'comment': '用户账号管理表'}
    
    # 主键
    UserID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="用户ID"
    )
    
    # 基本信息
    Username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="用户名"
    )
    
    PasswordHash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希（Argon2id或Bcrypt）"
    )
    
    RealName: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="真实姓名"
    )
    
    Position: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="职位"
    )
    
    Role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user",
        comment="角色：admin-管理员，user-普通用户"
    )
    
    Email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="邮箱"
    )
    
    IsActive: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="是否激活（1:是，0:否）"
    )
    
    # 时间戳
    CreatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="创建时间"
    )
    
    LastLogin: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
    )
    
    # 备用字段（暂时注释，数据库中可能不存在）
    # ReservedField1: Mapped[Optional[str]] = mapped_column(
    #     String(500),
    #     nullable=True,
    #     comment="备用字段1（原Session令牌，JWT中不再使用）"
    # )
    
    # ReservedField2: Mapped[Optional[str]] = mapped_column(
    #     String(500),
    #     nullable=True,
    #     comment="备用字段2"
    # )
    
    def __repr__(self) -> str:
        return f"<User {self.Username} ({self.Role})>"

