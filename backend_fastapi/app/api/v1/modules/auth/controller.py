# -*- coding: utf-8 -*-
"""
用户认证Controller
API路由层 - 处理HTTP请求
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id, get_current_user_with_role
from app.common.response import SuccessResponse
from app.api.v1.modules.auth.service import AuthService, UserManagementService
from app.api.v1.modules.auth.schema import (
    LoginRequest,
    RegisterRequest,
    ChangePasswordRequest,
    UpdateProfileRequest,
    LoginResponse,
    UserInfoResponse,
    CreateUserRequest,
    UpdateUserRequest,
    ResetPasswordRequest,
    UserListResponse
)


# 创建路由
router = APIRouter()


@router.post(
    "/login",
    response_model=None,
    summary="用户登录",
    description="用户登录接口，返回JWT令牌"
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    
    返回:
    - **access_token**: 访问令牌
    - **refresh_token**: 刷新令牌
    - **user**: 用户信息
    """
    result = await AuthService.login(db, login_data)
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="登录成功"
    )


@router.post(
    "/register",
    response_model=None,
    summary="用户注册",
    description="用户注册接口"
)
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    - **username**: 用户名（3-50字符，仅字母数字下划线）
    - **password**: 密码（6-128字符）
    - **real_name**: 真实姓名（可选）
    - **email**: 邮箱（可选）
    """
    result = await AuthService.register(db, register_data)
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="注册成功"
    )


@router.get(
    "/current/info",
    response_model=None,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息"
)
async def get_current_user_info(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户信息
    
    需要认证: 是
    """
    result = await AuthService.get_current_user_info(db, user_id)
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="获取成功"
    )


@router.put(
    "/current/profile",
    response_model=None,
    summary="更新个人信息",
    description="更新当前用户的个人信息"
)
async def update_profile(
    profile_data: UpdateProfileRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    更新个人信息
    
    需要认证: 是
    
    - **real_name**: 真实姓名
    - **position**: 职位
    - **email**: 邮箱
    """
    result = await AuthService.update_profile(db, user_id, profile_data)
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="更新成功"
    )


@router.put(
    "/current/password",
    response_model=None,
    summary="修改密码",
    description="修改当前用户密码"
)
async def change_password(
    password_data: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    
    需要认证: 是
    
    - **old_password**: 旧密码
    - **new_password**: 新密码
    """
    await AuthService.change_password(db, user_id, password_data)
    return SuccessResponse(
        data=None,
        msg="密码修改成功，请重新登录"
    )


# ==================== 用户管理API（仅管理员） ====================

@router.get(
    "/users",
    response_model=None,
    summary="获取用户列表",
    description="获取用户列表（仅管理员）"
)
async def get_user_list(
    page: int = 1,
    page_size: int = 10,
    username: str = None,
    role: str = None,
    is_active: bool = None,
    current_user: dict = Depends(get_current_user_with_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户列表
    
    需要认证: 是
    需要权限: 管理员
    """
    result = await UserManagementService.get_user_list(
        db, page, page_size, username, role, is_active
    )
    return SuccessResponse(
        data=result,
        msg="获取成功"
    )


@router.post(
    "/users",
    response_model=None,
    summary="创建用户",
    description="创建新用户（仅管理员）"
)
async def create_user(
    user_data: CreateUserRequest,
    current_user: dict = Depends(get_current_user_with_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    创建用户
    
    需要认证: 是
    需要权限: 管理员
    """
    result = await UserManagementService.create_user(
        db=db,
        username=user_data.username,
        password=user_data.password,
        real_name=user_data.real_name,
        position=user_data.position,
        email=user_data.email,
        role=user_data.role
    )
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="创建成功"
    )


@router.put(
    "/users/{user_id}",
    response_model=None,
    summary="更新用户信息",
    description="更新用户信息（仅管理员）"
)
async def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    current_user: dict = Depends(get_current_user_with_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户信息
    
    需要认证: 是
    需要权限: 管理员
    """
    result = await UserManagementService.update_user(
        db=db,
        user_id=user_id,
        real_name=user_data.real_name,
        position=user_data.position,
        email=user_data.email,
        role=user_data.role,
        is_active=user_data.is_active
    )
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="更新成功"
    )


@router.delete(
    "/users/{user_id}",
    response_model=None,
    summary="删除用户",
    description="删除用户（仅管理员）"
)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user_with_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    删除用户
    
    需要认证: 是
    需要权限: 管理员
    """
    await UserManagementService.delete_user(db, user_id)
    return SuccessResponse(
        data=None,
        msg="删除成功"
    )


@router.put(
    "/users/{user_id}/reset-password",
    response_model=None,
    summary="重置用户密码",
    description="重置用户密码（仅管理员）"
)
async def reset_user_password(
    user_id: int,
    password_data: ResetPasswordRequest,
    current_user: dict = Depends(get_current_user_with_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    重置用户密码
    
    需要认证: 是
    需要权限: 管理员
    """
    await UserManagementService.reset_password(db, user_id, password_data.new_password)
    return SuccessResponse(
        data=None,
        msg="密码重置成功"
    )

