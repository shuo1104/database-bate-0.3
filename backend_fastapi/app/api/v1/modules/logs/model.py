# -*- coding: utf-8 -*-
"""
系统日志模型
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SystemInfoModel(Base):
    """
    系统信息模型
    记录系统首次启动时间等全局信息
    """
    __tablename__ = "tbl_SystemInfo"
    __table_args__ = {'comment': '系统信息表'}
    
    # 主键
    InfoID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="信息ID"
    )
    
    # 系统首次启动时间
    FirstStartTime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="系统首次启动时间"
    )
    
    # 系统版本
    Version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="系统版本"
    )
    
    # 最后更新时间
    LastUpdateTime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="最后更新时间"
    )


class UserLoginLogModel(Base):
    """
    用户登录日志模型
    记录用户登录和登出时间
    """
    __tablename__ = "tbl_UserLoginLogs"
    __table_args__ = {'comment': '用户登录日志表'}
    
    # 主键
    LogID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="日志ID"
    )
    
    # 用户信息
    UserID: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    Username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="用户名"
    )
    
    # 登录信息
    LoginTime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
        comment="登录时间"
    )
    
    LogoutTime: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="登出时间"
    )
    
    # 使用时长（秒）
    Duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="使用时长（秒）"
    )
    
    # IP地址
    IPAddress: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="登录IP地址"
    )
    
    # 用户代理
    UserAgent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="用户代理信息"
    )
    
    # 是否在线
    IsOnline: Mapped[bool] = mapped_column(
        Integer,
        nullable=False,
        default=True,
        comment="是否在线（1:是，0:否）"
    )
    
    # 最后心跳时间
    LastHeartbeat: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="最后心跳时间"
    )


class UserRegistrationLogModel(Base):
    """
    用户注册日志模型
    记录用户注册信息
    """
    __tablename__ = "tbl_UserRegistrationLogs"
    __table_args__ = {'comment': '用户注册日志表'}
    
    # 主键
    LogID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="日志ID"
    )
    
    # 用户信息
    UserID: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    Username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="用户名"
    )
    
    # 注册信息
    RegistrationTime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
        comment="注册时间"
    )
    
    RealName: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="真实姓名"
    )
    
    Position: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="职位"
    )
    
    Email: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="邮箱"
    )
    
    Role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user",
        comment="角色"
    )
    
    # IP地址
    IPAddress: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="注册IP地址"
    )
