# -*- coding: utf-8 -*-
"""
系统日志Schema
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ========== 登录日志相关 ==========
class LoginLogResponse(BaseModel):
    """登录日志响应"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    log_id: int = Field(..., alias="LogID", description="日志ID")
    user_id: int = Field(..., alias="UserID", description="用户ID")
    username: str = Field(..., alias="Username", description="用户名")
    login_time: str = Field(..., alias="LoginTime", description="登录时间")  # 改为 str
    logout_time: Optional[str] = Field(None, alias="LogoutTime", description="登出时间")  # 改为 str
    duration: Optional[int] = Field(None, alias="Duration", description="使用时长（秒）")
    ip_address: Optional[str] = Field(None, alias="IPAddress", description="IP地址")
    user_agent: Optional[str] = Field(None, alias="UserAgent", description="用户代理")


class LoginLogListQuery(BaseModel):
    """登录日志列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    username: Optional[str] = Field(None, description="用户名")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")


class LoginLogListResponse(BaseModel):
    """登录日志列表响应"""
    items: List[LoginLogResponse]
    total: int
    page: int
    page_size: int


# ========== 注册日志相关 ==========
class RegistrationLogResponse(BaseModel):
    """注册日志响应"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    log_id: int = Field(..., alias="LogID", description="日志ID")
    user_id: int = Field(..., alias="UserID", description="用户ID")
    username: str = Field(..., alias="Username", description="用户名")
    registration_time: str = Field(..., alias="RegistrationTime", description="注册时间")  # 改为 str
    real_name: Optional[str] = Field(None, alias="RealName", description="真实姓名")
    position: Optional[str] = Field(None, alias="Position", description="职位")
    email: Optional[str] = Field(None, alias="Email", description="邮箱")
    role: str = Field(..., alias="Role", description="角色")
    ip_address: Optional[str] = Field(None, alias="IPAddress", description="IP地址")


class RegistrationLogListQuery(BaseModel):
    """注册日志列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    username: Optional[str] = Field(None, description="用户名")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")


class RegistrationLogListResponse(BaseModel):
    """注册日志列表响应"""
    items: List[RegistrationLogResponse]
    total: int
    page: int
    page_size: int


# ========== 系统统计相关 ==========
class SystemStatisticsResponse(BaseModel):
    """系统统计响应"""
    model_config = ConfigDict(from_attributes=True)
    
    system_uptime_days: int = Field(..., description="系统运行天数")
    system_start_date: str = Field(..., description="系统启动日期")  # 改为 str，在 service 层转换
    total_users: int = Field(..., description="总用户数")
    total_projects: int = Field(..., description="总项目数")
    total_materials: int = Field(..., description="总原料数")
    total_fillers: int = Field(..., description="总填料数")
    total_logins_today: int = Field(..., description="今日登录次数")
    active_users_today: int = Field(..., description="今日活跃用户数")
    total_usage_time_today: int = Field(..., description="今日总使用时长（秒）")


class DailyUsageStatistics(BaseModel):
    """每日使用统计"""
    date: str = Field(..., description="日期（YYYY-MM-DD）")
    login_count: int = Field(..., description="登录次数")
    active_users: int = Field(..., description="活跃用户数")
    total_duration: int = Field(..., description="总使用时长（秒）")
    avg_duration: float = Field(..., description="平均使用时长（秒）")


class DailyUsageListQuery(BaseModel):
    """每日使用统计查询参数"""
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    days: int = Field(30, ge=1, le=365, description="统计天数（默认30天）")


class DailyUsageListResponse(BaseModel):
    """每日使用统计列表响应"""
    items: List[DailyUsageStatistics]

