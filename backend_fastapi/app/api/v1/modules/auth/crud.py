# -*- coding: utf-8 -*-
"""
用户CRUD操作
数据访问层 - 负责数据库操作
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, update, delete, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.v1.modules.auth.model import UserModel
from app.core.logger import logger


class UserCRUD:
    """用户CRUD操作类"""
    
    @staticmethod
    async def get_by_username(
        db: AsyncSession,
        username: str
    ) -> Optional[UserModel]:
        """
        根据用户名查询用户
        
        Args:
            db: 数据库会话
            username: 用户名
        
        Returns:
            用户对象或None
        """
        try:
            stmt = select(UserModel).where(UserModel.Username == username)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"queryuserfailed: {e}")
            raise
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        user_id: int
    ) -> Optional[UserModel]:
        """
        根据ID查询用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            用户对象或None
        """
        try:
            stmt = select(UserModel).where(UserModel.UserID == user_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"queryuserfailed: {e}")
            raise
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        password_hash: str,
        real_name: Optional[str] = None,
        position: Optional[str] = None,
        email: Optional[str] = None,
        role: str = "user"
    ) -> UserModel:
        """
        创建新用户
        
        Args:
            db: 数据库会话
            username: 用户名
            password_hash: 密码哈希
            real_name: 真实姓名
            position: 职位
            email: 邮箱
            role: 角色
        
        Returns:
            创建的用户对象
        """
        try:
            user = UserModel(
                Username=username,
                PasswordHash=password_hash,
                RealName=real_name,
                Position=position,
                Email=email,
                Role=role,
                IsActive=1  # 使用整数而不是布尔值（数据库中是SMALLINT）
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"createuserfailed: {e}")
            raise
    
    @staticmethod
    async def update_password(
        db: AsyncSession,
        user_id: int,
        new_password_hash: str
    ) -> bool:
        """
        更新用户密码
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            new_password_hash: 新密码哈希
        
        Returns:
            是否成功
        """
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.UserID == user_id)
                .values(PasswordHash=new_password_hash)
            )
            await db.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"update密码failed: {e}")
            return False
    
    @staticmethod
    async def update_last_login(
        db: AsyncSession,
        user_id: int
    ) -> bool:
        """
        更新最后登录时间
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            是否成功
        """
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.UserID == user_id)
                .values(LastLogin=datetime.now())
            )
            await db.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"update登录时间failed: {e}")
            return False
    
    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: int,
        real_name: Optional[str] = None,
        position: Optional[str] = None,
        email: Optional[str] = None
    ) -> bool:
        """
        更新用户个人信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            real_name: 真实姓名
            position: 职位
            email: 邮箱
        
        Returns:
            是否成功
        """
        try:
            values = {}
            if real_name is not None:
                values["RealName"] = real_name
            if position is not None:
                values["Position"] = position
            if email is not None:
                values["Email"] = email
            
            if values:
                stmt = (
                    update(UserModel)
                    .where(UserModel.UserID == user_id)
                    .values(**values)
                )
                await db.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"update个人信息failed: {e}")
            return False
    
    @staticmethod
    async def get_list_paginated(
        db: AsyncSession,
        page: int,
        page_size: int,
        username: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[UserModel], int]:
        """
        分页查询用户列表
        
        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            username: 用户名（模糊搜索）
            role: 角色
            is_active: 是否激活
        
        Returns:
            用户列表和总数
        """
        try:
            # 构建查询条件
            conditions = []
            if username:
                conditions.append(
                    or_(
                        UserModel.Username.like(f"%{username}%"),
                        UserModel.RealName.like(f"%{username}%")
                    )
                )
            if role:
                conditions.append(UserModel.Role == role)
            if is_active is not None:
                conditions.append(UserModel.IsActive == (1 if is_active else 0))  # 转换布尔值为整数
            
            # 查询总数
            count_stmt = select(func.count()).select_from(UserModel)
            if conditions:
                count_stmt = count_stmt.where(*conditions)
            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()
            
            # 查询列表
            stmt = select(UserModel)
            if conditions:
                stmt = stmt.where(*conditions)
            stmt = stmt.order_by(UserModel.CreatedAt.desc())
            stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            
            result = await db.execute(stmt)
            users = result.scalars().all()
            
            return list(users), total
        except Exception as e:
            logger.error(f"分页queryuserfailed: {e}")
            raise
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        real_name: Optional[str] = None,
        position: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """
        更新用户信息（管理员使用）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            real_name: 真实姓名
            position: 职位
            email: 邮箱
            role: 角色
            is_active: 是否激活
        
        Returns:
            是否成功
        """
        try:
            values = {}
            if real_name is not None:
                values["RealName"] = real_name
            if position is not None:
                values["Position"] = position
            if email is not None:
                values["Email"] = email
            if role is not None:
                values["Role"] = role
            if is_active is not None:
                values["IsActive"] = 1 if is_active else 0  # 转换布尔值为整数
            
            if values:
                stmt = (
                    update(UserModel)
                    .where(UserModel.UserID == user_id)
                    .values(**values)
                )
                await db.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"updateuser信息failed: {e}")
            return False
    
    @staticmethod
    async def delete_user(
        db: AsyncSession,
        user_id: int
    ) -> bool:
        """
        删除用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            是否成功
        """
        try:
            stmt = delete(UserModel).where(UserModel.UserID == user_id)
            await db.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"deleteduserfailed: {e}")
            return False

