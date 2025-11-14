# -*- coding: utf-8 -*-
"""
系统日志Controller层
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user_with_role, get_current_user_id
from app.common.response import SuccessResponse
from .service import LogService
from .schema import (
    LoginLogListQuery,
    RegistrationLogListQuery,
    DailyUsageListQuery
)

router = APIRouter(prefix="/logs", tags=["系统日志"])


@router.get("/statistics", summary="获取系统统计信息")
async def get_system_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_with_role("admin"))
):
    """
    获取系统统计信息（仅管理员）
    - 系统运行天数
    - 总用户数、总数据量
    - 今日登录和使用统计
    """
    stats = await LogService.get_system_statistics(db)
    return SuccessResponse(data=stats.model_dump())


@router.get("/login", summary="获取登录日志列表")
async def get_login_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_with_role("admin"))
):
    """
    获取登录日志列表（仅管理员）
    - 支持按用户名、日期范围筛选
    - 支持分页
    """
    query = LoginLogListQuery(
        page=page,
        page_size=page_size,
        username=username,
        start_date=start_date,
        end_date=end_date
    )
    result = await LogService.get_login_logs(db, query)
    return SuccessResponse(data=result.model_dump())


@router.get("/registration", summary="获取注册日志列表")
async def get_registration_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_with_role("admin"))
):
    """
    获取注册日志列表（仅管理员）
    - 支持按用户名、日期范围筛选
    - 支持分页
    """
    query = RegistrationLogListQuery(
        page=page,
        page_size=page_size,
        username=username,
        start_date=start_date,
        end_date=end_date
    )
    result = await LogService.get_registration_logs(db, query)
    return SuccessResponse(data=result.model_dump())


@router.get("/daily-usage", summary="获取每日使用统计")
async def get_daily_usage_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_with_role("admin"))
):
    """
    获取每日使用统计（仅管理员）
    - 每日登录次数
    - 每日活跃用户数
    - 每日总使用时长和平均使用时长
    """
    query = DailyUsageListQuery(
        days=days,
        start_date=start_date,
        end_date=end_date
    )
    result = await LogService.get_daily_usage_statistics(db, query)
    return SuccessResponse(data=result.model_dump())


@router.post("/heartbeat/{log_id}", summary="更新心跳")
async def update_heartbeat(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    更新心跳时间（任何登录用户）
    - 自动更新使用时长
    - 前端应该每1-5分钟调用一次
    """
    success = await LogService.update_heartbeat(db, log_id)
    return SuccessResponse(data={"success": success}, msg="心跳更新成功")


@router.post("/logout/{log_id}", summary="用户登出")
async def user_logout(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    记录用户登出（任何登录用户）
    - 更新登出时间
    - 计算使用时长
    """
    success = await LogService.record_logout(db, log_id)
    return SuccessResponse(data={"success": success}, msg="登出成功")

