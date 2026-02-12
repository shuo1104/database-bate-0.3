# -*- coding: utf-8 -*-
"""
用户认证Service
业务逻辑层 - 处理业务逻辑
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.auth.crud import UserCRUD
from app.api.v1.modules.auth.schema import (
    LoginRequest,
    RegisterRequest,
    ChangePasswordRequest,
    UpdateProfileRequest,
    TokenResponse,
    UserInfoResponse,
    LoginResponse
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)
from app.config.settings import settings
from app.core.logger import logger
from app.api.v1.modules.logs.service import LogService
from app.core.custom_exceptions import (
    AuthenticationException,
    AuthorizationException,
    RecordNotFoundException,
    DuplicateRecordException,
    BusinessLogicException,
    DatabaseException,
)


class AuthService:
    """认证服务类"""
    
    @staticmethod
    async def login(
        db: AsyncSession,
        login_data: LoginRequest
    ) -> LoginResponse:
        """
        用户登录
        
        Args:
            db: 数据库会话
            login_data: 登录请求数据
        
        Returns:
            登录响应（令牌和用户信息）
        
        Raises:
            HTTPException: 登录失败
        """
        # 查询用户
        user = await UserCRUD.get_by_username(db, login_data.username)
        
        if not user:
            logger.warning(f"Login failed: Username does not exist - {login_data.username}")
            raise AuthenticationException("Incorrect username or password")
        
        # 检查用户是否激活（IsActive是整数：1-激活，0-禁用）
        if user.IsActive == 0:
            logger.warning(f"Login failed: Account disabled - {login_data.username}")
            raise AuthorizationException("Account has been disabled, please contact administrator")
        
        # 验证密码
        if not verify_password(login_data.password, user.PasswordHash):
            logger.warning(f"Login failed: Incorrect password - {login_data.username}")
            raise AuthenticationException("Incorrect username or password")
        
        # 生成JWT令牌
        token_data = {
            "user_id": user.UserID,
            "username": user.Username,
            "role": user.Role
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # 更新最后登录时间
        await UserCRUD.update_last_login(db, user.UserID)
        
        # 记录登录日志
        log_id = None
        try:
            log_id = await LogService.record_login(
                db=db,
                user_id=user.UserID,
                username=user.Username,
                ip_address=None,  # 可以从Request中获取
                user_agent=None   # 可以从Request headers中获取
            )
        except Exception as e:
            # 日志记录失败不影响登录流程，仅记录错误
            logger.error(f"记录登录日志failed: {type(e).__name__}: {e}", exc_info=True)
        
        await db.commit()
        
        logger.info(f"user登录successful: {login_data.username}")
        
        # 返回登录响应
        return LoginResponse(
            token=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            ),
            user=UserInfoResponse.model_validate(user),
            log_id=log_id
        )
    
    @staticmethod
    async def register(
        db: AsyncSession,
        register_data: RegisterRequest
    ) -> UserInfoResponse:
        """
        用户注册
        
        Args:
            db: 数据库会话
            register_data: 注册请求数据
        
        Returns:
            用户信息
        
        Raises:
            HTTPException: 注册失败
        """
        # 检查用户名是否已存在
        existing_user = await UserCRUD.get_by_username(db, register_data.username)
        if existing_user:
            logger.warning(f"Registration failed: Username already exists - {register_data.username}")
            raise DuplicateRecordException("User", "username", register_data.username)
        
        # 创建用户
        password_hash = hash_password(register_data.password)
        user = await UserCRUD.create_user(
            db=db,
            username=register_data.username,
            password_hash=password_hash,
            real_name=register_data.real_name,
            email=register_data.email
        )
        
        # 记录注册日志
        try:
            await LogService.record_registration(
                db=db,
                user_id=user.UserID,
                username=user.Username,
                real_name=user.RealName,
                position=user.Position,
                email=user.Email,
                role=user.Role,
                ip_address=None  # 可以从Request中获取
            )
        except Exception as e:
            # 日志记录失败不影响注册流程，仅记录错误
            logger.error(f"记录注册日志failed: {type(e).__name__}: {e}", exc_info=True)
        
        await db.commit()
        
        logger.info(f"user注册successful: {register_data.username}")
        
        return UserInfoResponse.model_validate(user)
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: int,
        password_data: ChangePasswordRequest
    ) -> bool:
        """
        修改密码
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            password_data: 密码修改数据
        
        Returns:
            是否成功
        
        Raises:
            HTTPException: 修改失败
        """
        # 查询用户
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            raise RecordNotFoundException("User", user_id)
        
        # 验证旧密码
        if not verify_password(password_data.old_password, user.PasswordHash):
            logger.warning(f"Password change failed: Incorrect old password - UserID:{user_id}")
            raise BusinessLogicException("Incorrect old password")
        
        # 更新密码
        new_password_hash = hash_password(password_data.new_password)
        success = await UserCRUD.update_password(db, user_id, new_password_hash)
        await db.commit()
        
        if success:
            logger.info(f"Password changed successfully - UserID:{user_id}")
        
        return success
    
    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: int,
        profile_data: UpdateProfileRequest
    ) -> UserInfoResponse:
        """
        更新个人信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            profile_data: 个人信息数据
        
        Returns:
            更新后的用户信息
        
        Raises:
            HTTPException: 更新失败
        """
        # 查询用户
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            raise RecordNotFoundException("User", user_id)
        
        # 更新信息
        success = await UserCRUD.update_profile(
            db=db,
            user_id=user_id,
            real_name=profile_data.real_name,
            position=profile_data.position,
            email=profile_data.email
        )
        await db.commit()
        
        if not success:
            raise DatabaseException("Failed to update user profile")
        
        # 刷新用户信息
        await db.refresh(user)
        logger.info(f"Profile updated successfully - UserID:{user_id}")
        
        return UserInfoResponse.model_validate(user)
    
    @staticmethod
    async def get_current_user_info(
        db: AsyncSession,
        user_id: int
    ) -> UserInfoResponse:
        """
        获取当前用户信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            用户信息
        
        Raises:
            RecordNotFoundException: 用户不存在
        """
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            raise RecordNotFoundException("User", user_id)
        
        return UserInfoResponse.model_validate(user)


class UserManagementService:
    """用户管理服务类（仅管理员）"""
    
    @staticmethod
    async def get_user_list(
        db: AsyncSession,
        page: int,
        page_size: int,
        username: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ):
        """
        获取用户列表
        
        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            username: 用户名
            role: 角色
            is_active: 是否激活
        
        Returns:
            用户列表和总数
        """
        users, total = await UserCRUD.get_list_paginated(
            db, page, page_size, username, role, is_active
        )
        
        return {
            "items": [UserInfoResponse.model_validate(u).model_dump(mode='json') for u in users],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        password: str,
        real_name: Optional[str] = None,
        position: Optional[str] = None,
        email: Optional[str] = None,
        role: str = "user"
    ) -> UserInfoResponse:
        """
        创建用户
        
        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
            real_name: 真实姓名
            position: 职位
            email: 邮箱
            role: 角色
        
        Returns:
            用户信息
        
        Raises:
            HTTPException: 创建失败
        """
        # 检查用户名是否已存在
        existing_user = await UserCRUD.get_by_username(db, username)
        if existing_user:
            raise DuplicateRecordException("User", "username", username)
        
        # 创建用户
        password_hash = hash_password(password)
        user = await UserCRUD.create_user(
            db=db,
            username=username,
            password_hash=password_hash,
            real_name=real_name,
            position=position,
            email=email,
            role=role
        )
        
        # 创建注册日志
        try:
            from app.api.v1.modules.logs.crud import LogCRUD
            await LogCRUD.create_registration_log(
                db=db,
                user_id=user.UserID,
                username=username,
                real_name=real_name,
                position=position,
                email=email,
                role=role,
                ip_address=None  # TODO: 可以从请求中获取IP地址
            )
        except Exception as e:
            # 日志记录失败不影响用户创建，仅记录错误
            logger.warning(f"create注册日志failed: {type(e).__name__}: {e}", exc_info=False)
        
        await db.commit()
        
        return UserInfoResponse.model_validate(user)
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        real_name: Optional[str] = None,
        position: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> UserInfoResponse:
        """
        更新用户信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            real_name: 真实姓名
            position: 职位
            email: 邮箱
            role: 角色
            is_active: 是否激活
        
        Returns:
            用户信息
        
        Raises:
            HTTPException: 更新失败
        """
        # 检查用户是否存在
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            raise RecordNotFoundException("User", user_id)
        
        # 更新用户信息
        success = await UserCRUD.update_user(
            db=db,
            user_id=user_id,
            real_name=real_name,
            position=position,
            email=email,
            role=role,
            is_active=is_active
        )
        
        if not success:
            raise DatabaseException("Failed to update user")
        
        await db.commit()
        await db.refresh(user)
        
        return UserInfoResponse.model_validate(user)
    
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
        
        Raises:
            HTTPException: 删除失败
        """
        # 检查用户是否存在
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            raise RecordNotFoundException("User", user_id)
        
        # 删除用户
        success = await UserCRUD.delete_user(db, user_id)
        if not success:
            raise DatabaseException("Failed to delete user")
        
        await db.commit()
        return True
    
    @staticmethod
    async def reset_password(
        db: AsyncSession,
        user_id: int,
        new_password: str
    ) -> bool:
        """
        重置用户密码
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            new_password: 新密码
        
        Returns:
            是否成功
        
        Raises:
            HTTPException: 重置失败
        """
        # 检查用户是否存在
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            raise RecordNotFoundException("User", user_id)
        
        # 重置密码
        password_hash = hash_password(new_password)
        success = await UserCRUD.update_password(db, user_id, password_hash)
        
        if not success:
            raise DatabaseException("Failed to reset password")
        
        await db.commit()
        return True