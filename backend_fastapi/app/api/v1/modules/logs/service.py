# -*- coding: utf-8 -*-
"""
系统日志Service层
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import LogCRUD
from .schema import (
    LoginLogListQuery,
    LoginLogListResponse,
    LoginLogResponse,
    RegistrationLogListQuery,
    RegistrationLogListResponse,
    RegistrationLogResponse,
    SystemStatisticsResponse,
    DailyUsageListQuery,
    DailyUsageListResponse,
    DailyUsageStatistics
)


class LogService:
    """日志服务类"""
    
    @staticmethod
    async def get_login_logs(
        db: AsyncSession,
        query: LoginLogListQuery
    ) -> LoginLogListResponse:
        """获取登录日志列表"""
        items, total = await LogCRUD.get_login_logs_paginated(
            db=db,
            page=query.page,
            page_size=query.page_size,
            username=query.username,
            start_date=query.start_date,
            end_date=query.end_date
        )
        
        # 转换 datetime 为字符串
        converted_items = []
        for item in items:
            item_dict = {
                'LogID': item.LogID,
                'UserID': item.UserID,
                'Username': item.Username,
                'LoginTime': item.LoginTime.isoformat() if item.LoginTime else None,
                'LogoutTime': item.LogoutTime.isoformat() if item.LogoutTime else None,
                'Duration': item.Duration,
                'IPAddress': item.IPAddress,
                'UserAgent': item.UserAgent,
            }
            converted_items.append(LoginLogResponse.model_validate(item_dict))
        
        return LoginLogListResponse(
            items=converted_items,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    @staticmethod
    async def get_registration_logs(
        db: AsyncSession,
        query: RegistrationLogListQuery
    ) -> RegistrationLogListResponse:
        """获取注册日志列表"""
        items, total = await LogCRUD.get_registration_logs_paginated(
            db=db,
            page=query.page,
            page_size=query.page_size,
            username=query.username,
            start_date=query.start_date,
            end_date=query.end_date
        )
        
        # 转换 datetime 为字符串
        converted_items = []
        for item in items:
            item_dict = {
                'LogID': item.LogID,
                'UserID': item.UserID,
                'Username': item.Username,
                'RegistrationTime': item.RegistrationTime.isoformat() if item.RegistrationTime else None,
                'RealName': item.RealName,
                'Position': item.Position,
                'Email': item.Email,
                'Role': item.Role,
                'IPAddress': item.IPAddress,
            }
            converted_items.append(RegistrationLogResponse.model_validate(item_dict))
        
        return RegistrationLogListResponse(
            items=converted_items,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    @staticmethod
    async def get_system_statistics(
        db: AsyncSession
    ) -> SystemStatisticsResponse:
        """获取系统统计信息"""
        stats = await LogCRUD.get_system_statistics(db)
        # 转换 datetime 为字符串
        if isinstance(stats.get('system_start_date'), datetime):
            stats['system_start_date'] = stats['system_start_date'].isoformat()
        return SystemStatisticsResponse(**stats)
    
    @staticmethod
    async def get_daily_usage_statistics(
        db: AsyncSession,
        query: DailyUsageListQuery
    ) -> DailyUsageListResponse:
        """获取每日使用统计"""
        stats = await LogCRUD.get_daily_usage_statistics(
            db=db,
            days=query.days,
            start_date=query.start_date,
            end_date=query.end_date
        )
        
        return DailyUsageListResponse(
            items=[DailyUsageStatistics(**item) for item in stats]
        )
    
    @staticmethod
    async def record_login(
        db: AsyncSession,
        user_id: int,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> int:
        """记录用户登录"""
        log = await LogCRUD.create_login_log(
            db=db,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return log.LogID
    
    @staticmethod
    async def record_logout(
        db: AsyncSession,
        log_id: int
    ) -> bool:
        """记录用户登出"""
        log = await LogCRUD.update_logout_log(db=db, log_id=log_id)
        return log is not None
    
    @staticmethod
    async def logout_by_user_id(
        db: AsyncSession,
        user_id: int
    ) -> bool:
        """根据用户ID登出（用于强制登出）"""
        return await LogCRUD.logout_by_user_id(db=db, user_id=user_id)
    
    @staticmethod
    async def update_heartbeat(
        db: AsyncSession,
        log_id: int
    ) -> bool:
        """更新心跳时间"""
        log = await LogCRUD.update_heartbeat(db=db, log_id=log_id)
        return log is not None
    
    @staticmethod
    async def record_registration(
        db: AsyncSession,
        user_id: int,
        username: str,
        real_name: Optional[str] = None,
        position: Optional[str] = None,
        email: Optional[str] = None,
        role: str = "user",
        ip_address: Optional[str] = None
    ) -> int:
        """记录用户注册"""
        log = await LogCRUD.create_registration_log(
            db=db,
            user_id=user_id,
            username=username,
            real_name=real_name,
            position=position,
            email=email,
            role=role,
            ip_address=ip_address
        )
        return log.LogID

