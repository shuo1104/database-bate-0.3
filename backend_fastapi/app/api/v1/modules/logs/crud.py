# -*- coding: utf-8 -*-
"""
系统日志CRUD操作
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import func, select, and_, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from .model import UserLoginLogModel, UserRegistrationLogModel, SystemInfoModel
from ..projects.model import ProjectModel
from ..materials.model import MaterialModel
from ..fillers.model import FillerModel
from ..auth.model import UserModel


class LogCRUD:
    """日志CRUD操作类"""
    
    @staticmethod
    async def get_or_create_system_info(db: AsyncSession) -> SystemInfoModel:
        """获取或创建系统信息"""
        stmt = select(SystemInfoModel).limit(1)
        result = await db.execute(stmt)
        system_info = result.scalar_one_or_none()
        
        if not system_info:
            system_info = SystemInfoModel(
                FirstStartTime=datetime.now(),
                Version="1.0.0"
            )
            db.add(system_info)
            await db.commit()
            await db.refresh(system_info)
        
        return system_info
    
    @staticmethod
    async def create_login_log(
        db: AsyncSession,
        user_id: int,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserLoginLogModel:
        """创建登录日志"""
        log = UserLoginLogModel(
            UserID=user_id,
            Username=username,
            LoginTime=datetime.now(),
            IPAddress=ip_address,
            UserAgent=user_agent,
            IsOnline=True,
            LastHeartbeat=datetime.now()
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
    
    @staticmethod
    async def update_logout_log(
        db: AsyncSession,
        log_id: int
    ) -> Optional[UserLoginLogModel]:
        """更新登出时间和使用时长"""
        stmt = select(UserLoginLogModel).where(UserLoginLogModel.LogID == log_id)
        result = await db.execute(stmt)
        log = result.scalar_one_or_none()
        
        if log:
            log.LogoutTime = datetime.now()
            log.IsOnline = False
            if log.LoginTime:
                log.Duration = int((log.LogoutTime - log.LoginTime).total_seconds())
            await db.commit()
            await db.refresh(log)
        
        return log
    
    @staticmethod
    async def update_heartbeat(
        db: AsyncSession,
        log_id: int
    ) -> Optional[UserLoginLogModel]:
        """更新心跳时间"""
        stmt = select(UserLoginLogModel).where(UserLoginLogModel.LogID == log_id)
        result = await db.execute(stmt)
        log = result.scalar_one_or_none()
        
        if log:
            log.LastHeartbeat = datetime.now()
            # 自动更新使用时长
            if log.LoginTime:
                log.Duration = int((datetime.now() - log.LoginTime).total_seconds())
            await db.commit()
            await db.refresh(log)
        
        return log
    
    @staticmethod
    async def logout_by_user_id(
        db: AsyncSession,
        user_id: int
    ) -> bool:
        """根据用户ID登出（用于强制登出）"""
        stmt = select(UserLoginLogModel).where(
            and_(
                UserLoginLogModel.UserID == user_id,
                UserLoginLogModel.IsOnline == True
            )
        ).order_by(UserLoginLogModel.LoginTime.desc())
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        for log in logs:
            log.LogoutTime = datetime.now()
            log.IsOnline = False
            if log.LoginTime:
                log.Duration = int((log.LogoutTime - log.LoginTime).total_seconds())
        
        await db.commit()
        return len(logs) > 0
    
    @staticmethod
    async def get_login_logs_paginated(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[UserLoginLogModel], int]:
        """分页获取登录日志"""
        # 构建查询条件
        conditions = []
        if username:
            conditions.append(UserLoginLogModel.Username.like(f"%{username}%"))
        if start_date:
            conditions.append(UserLoginLogModel.LoginTime >= start_date)
        if end_date:
            conditions.append(UserLoginLogModel.LoginTime <= end_date)
        
        # 查询总数
        count_stmt = select(func.count()).select_from(UserLoginLogModel)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()
        
        # 查询数据
        stmt = select(UserLoginLogModel)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(UserLoginLogModel.LoginTime.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(stmt)
        items = result.scalars().all()
        
        return items, total
    
    @staticmethod
    async def create_registration_log(
        db: AsyncSession,
        user_id: int,
        username: str,
        real_name: Optional[str] = None,
        position: Optional[str] = None,
        email: Optional[str] = None,
        role: str = "user",
        ip_address: Optional[str] = None
    ) -> UserRegistrationLogModel:
        """创建注册日志"""
        log = UserRegistrationLogModel(
            UserID=user_id,
            Username=username,
            RegistrationTime=datetime.now(),
            RealName=real_name,
            Position=position,
            Email=email,
            Role=role,
            IPAddress=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
    
    @staticmethod
    async def get_registration_logs_paginated(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[UserRegistrationLogModel], int]:
        """分页获取注册日志"""
        # 构建查询条件
        conditions = []
        if username:
            conditions.append(UserRegistrationLogModel.Username.like(f"%{username}%"))
        if start_date:
            conditions.append(UserRegistrationLogModel.RegistrationTime >= start_date)
        if end_date:
            conditions.append(UserRegistrationLogModel.RegistrationTime <= end_date)
        
        # 查询总数
        count_stmt = select(func.count()).select_from(UserRegistrationLogModel)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()
        
        # 查询数据
        stmt = select(UserRegistrationLogModel)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(UserRegistrationLogModel.RegistrationTime.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(stmt)
        items = result.scalars().all()
        
        return items, total
    
    @staticmethod
    async def get_system_statistics(db: AsyncSession) -> dict:
        """获取系统统计信息"""
        # 获取或创建系统信息
        system_info = await LogCRUD.get_or_create_system_info(db)
        system_start_date = system_info.FirstStartTime
        
        # 计算系统运行天数
        system_uptime_days = (datetime.now() - system_start_date).days
        
        # 总用户数
        total_users_stmt = select(func.count()).select_from(UserModel)
        total_users_result = await db.execute(total_users_stmt)
        total_users = total_users_result.scalar()
        
        # 总项目数
        total_projects_stmt = select(func.count()).select_from(ProjectModel)
        total_projects_result = await db.execute(total_projects_stmt)
        total_projects = total_projects_result.scalar()
        
        # 总原料数
        total_materials_stmt = select(func.count()).select_from(MaterialModel)
        total_materials_result = await db.execute(total_materials_stmt)
        total_materials = total_materials_result.scalar()
        
        # 总填料数
        total_fillers_stmt = select(func.count()).select_from(FillerModel)
        total_fillers_result = await db.execute(total_fillers_stmt)
        total_fillers = total_fillers_result.scalar()
        
        # 今日登录次数
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        today_logins_stmt = select(func.count()).select_from(UserLoginLogModel).where(
            and_(
                UserLoginLogModel.LoginTime >= today_start,
                UserLoginLogModel.LoginTime < today_end
            )
        )
        today_logins_result = await db.execute(today_logins_stmt)
        total_logins_today = today_logins_result.scalar()
        
        # 今日活跃用户数
        active_users_stmt = select(func.count(distinct(UserLoginLogModel.UserID))).where(
            and_(
                UserLoginLogModel.LoginTime >= today_start,
                UserLoginLogModel.LoginTime < today_end
            )
        )
        active_users_result = await db.execute(active_users_stmt)
        active_users_today = active_users_result.scalar()
        
        # 今日总使用时长
        today_duration_stmt = select(func.sum(UserLoginLogModel.Duration)).where(
            and_(
                UserLoginLogModel.LoginTime >= today_start,
                UserLoginLogModel.LoginTime < today_end,
                UserLoginLogModel.Duration.isnot(None)
            )
        )
        today_duration_result = await db.execute(today_duration_stmt)
        total_usage_time_today = today_duration_result.scalar() or 0
        
        return {
            "system_uptime_days": system_uptime_days,
            "system_start_date": system_start_date,
            "total_users": total_users,
            "total_projects": total_projects,
            "total_materials": total_materials,
            "total_fillers": total_fillers,
            "total_logins_today": total_logins_today,
            "active_users_today": active_users_today,
            "total_usage_time_today": total_usage_time_today
        }
    
    @staticmethod
    async def get_daily_usage_statistics(
        db: AsyncSession,
        days: int = 30,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[dict]:
        """获取每日使用统计"""
        # 确定日期范围
        if not end_date:
            end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        if not start_date:
            start_date = end_date - timedelta(days=days)
        
        # 按日期分组统计
        stmt = select(
            func.date(UserLoginLogModel.LoginTime).label('date'),
            func.count(UserLoginLogModel.LogID).label('login_count'),
            func.count(distinct(UserLoginLogModel.UserID)).label('active_users'),
            func.sum(UserLoginLogModel.Duration).label('total_duration'),
            func.avg(UserLoginLogModel.Duration).label('avg_duration')
        ).where(
            and_(
                UserLoginLogModel.LoginTime >= start_date,
                UserLoginLogModel.LoginTime <= end_date
            )
        ).group_by(
            func.date(UserLoginLogModel.LoginTime)
        ).order_by(
            func.date(UserLoginLogModel.LoginTime).desc()
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        # 格式化结果
        statistics = []
        for row in rows:
            statistics.append({
                "date": row.date.strftime("%Y-%m-%d"),
                "login_count": row.login_count,
                "active_users": row.active_users,
                "total_duration": int(row.total_duration or 0),
                "avg_duration": float(row.avg_duration or 0)
            })
        
        return statistics

