# -*- coding: utf-8 -*-
"""
用户认证Schema
数据验证和序列化模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator
import re

from app.core.base_schema import BaseSchema, TimestampSchema


# ==================== 请求模型 ====================
class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=72, description="密码")
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=72, description="密码")
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v
    
    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v):
        """验证邮箱，空字符串转为None"""
        if v == "" or v is None:
            return None
        return v


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=72, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=72, description="新密码")


class UpdateProfileRequest(BaseModel):
    """更新个人信息请求"""
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    position: Optional[str] = Field(None, max_length=100, description="职位")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    
    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v):
        """验证邮箱，空字符串转为None"""
        if v == "" or v is None:
            return None
        return v


# ==================== 响应模型 ====================
class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class UserInfoResponse(BaseSchema):
    """用户信息响应"""
    user_id: int = Field(..., description="用户ID", alias="UserID")
    username: str = Field(..., description="用户名", alias="Username")
    real_name: Optional[str] = Field(None, description="真实姓名", alias="RealName")
    position: Optional[str] = Field(None, description="职位", alias="Position")
    role: str = Field(..., description="角色", alias="Role")
    email: Optional[str] = Field(None, description="邮箱", alias="Email")
    is_active: bool = Field(..., description="是否激活", alias="IsActive")
    created_at: Optional[datetime] = Field(None, description="创建时间", alias="CreatedAt")
    last_login: Optional[datetime] = Field(None, description="最后登录", alias="LastLogin")
    
    class Config:
        populate_by_name = True  # 允许使用别名
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class LoginResponse(BaseModel):
    """登录响应"""
    token: TokenResponse
    user: UserInfoResponse
    log_id: Optional[int] = Field(None, description="登录日志ID，用于心跳和登出")


# ==================== 用户管理相关模型 ====================
class UserListQuery(BaseModel):
    """用户列表查询参数"""
    page: int = Field(1, gt=0, description="页码")
    page_size: int = Field(10, gt=0, le=100, description="每页数量")
    username: Optional[str] = Field(None, description="用户名（模糊搜索）")
    role: Optional[str] = Field(None, description="角色")
    is_active: Optional[bool] = Field(None, description="是否激活")


class CreateUserRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=72, description="密码")
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    position: Optional[str] = Field(None, max_length=100, description="职位")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    role: str = Field("user", description="角色")
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v
    
    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v):
        """验证邮箱，空字符串转为None"""
        if v == "" or v is None:
            return None
        return v
    
    @field_validator("real_name", "position", mode="before")
    @classmethod
    def validate_optional_fields(cls, v):
        """验证可选字段，空字符串转为None"""
        if v == "":
            return None
        return v


class UpdateUserRequest(BaseModel):
    """更新用户请求"""
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    position: Optional[str] = Field(None, max_length=100, description="职位")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    role: Optional[str] = Field(None, description="角色")
    is_active: Optional[bool] = Field(None, description="是否激活")
    
    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v):
        """验证邮箱，空字符串转为None"""
        if v == "" or v is None:
            return None
        return v
    
    @field_validator("real_name", "position", mode="before")
    @classmethod
    def validate_optional_fields(cls, v):
        """验证可选字段，空字符串转为None"""
        if v == "":
            return None
        return v


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    new_password: str = Field(..., min_length=6, max_length=72, description="新密码")


class UserListResponse(BaseModel):
    """用户列表响应"""
    items: List[UserInfoResponse]
    total: int
    page: int
    page_size: int
