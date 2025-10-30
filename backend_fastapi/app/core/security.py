# -*- coding: utf-8 -*-
"""
安全认证模块
JWT令牌生成和验证、密码加密
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.settings import settings
from app.core.logger import logger
from app.core.custom_exceptions import (
    InvalidTokenException,
    AuthenticationException,
)


# ==================== 密码加密 ====================
# 支持 Bcrypt（新系统）和 Argon2（旧 Flask 系统）
pwd_context = CryptContext(
    schemes=["bcrypt", "argon2"],  # 优先使用bcrypt（更广泛支持）
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    密码哈希加密（优先使用 Argon2，支持更长密码）
    
    Args:
        password: 明文密码
    
    Returns:
        加密后的密码哈希
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码（仅支持 Bcrypt 和 Argon2 哈希密码）
    
    安全说明：
    - 强制要求密码必须是哈希存储
    - 不再支持明文密码（安全风险）
    - 如需迁移旧密码，请使用迁移脚本
    
    Args:
        plain_password: 明文密码
        hashed_password: 密码哈希（必须是 Bcrypt 或 Argon2 格式）
    
    Returns:
        密码是否匹配
    
    Raises:
        ValueError: 如果检测到明文密码存储
    """
    # 安全检查：拒绝明文密码
    if not hashed_password or not hashed_password.startswith('$'):
        logger.error(f"Security Warning: Illegal password format detected, verification refused")
        raise ValueError(
            "检测到非法密码格式。出于安全考虑，系统不再支持明文密码。"
            "请联系管理员运行密码迁移脚本或重置密码。"
        )
    
    # 使用 passlib 验证哈希密码（自动识别 Argon2 或 Bcrypt）
    try:
        is_valid = pwd_context.verify(plain_password, hashed_password)
        return is_valid
    except (ValueError, TypeError) as e:
        # 密码格式错误或类型错误
        logger.error(f"Password verification failed - Format error: {e}")
        return False
    except Exception as e:
        # 其他未预期的错误
        logger.error(f"Password verification failed - Unknown error: {type(e).__name__}: {e}", exc_info=True)
        return False


# ==================== JWT令牌 ====================
def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据字典
        expires_delta: 过期时间增量
    
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 要编码的数据字典
        expires_delta: 过期时间增量
    
    Returns:
        JWT刷新令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    解码JWT令牌
    
    Args:
        token: JWT令牌字符串
    
    Returns:
        解码后的数据字典
    
    Raises:
        HTTPException: 令牌无效或过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT decode failed: {e}")
        raise InvalidTokenException()


# ==================== HTTP Bearer认证 ====================
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    获取当前用户ID
    从JWT令牌中提取用户ID
    
    Args:
        credentials: HTTP认证凭据
    
    Returns:
        用户ID
    
    Raises:
        HTTPException: 认证失败
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise AuthenticationException("Invalid token: missing user information")
    
    return user_id


async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict[str, Any]:
    """
    获取当前用户完整信息
    
    Args:
        credentials: HTTP认证凭据
    
    Returns:
        用户信息字典
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    return {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "role": payload.get("role", "user")
    }


def get_current_user_with_role(required_role: str):
    """
    创建一个依赖函数，用于检查用户角色
    
    Args:
        required_role: 需要的角色
    
    Returns:
        依赖函数
    """
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict[str, Any]:
        """
        检查用户角色
        
        Args:
            credentials: HTTP认证凭据
        
        Returns:
            用户信息字典
        
        Raises:
            HTTPException: 权限不足
        """
        token = credentials.credentials
        payload = decode_token(token)
        
        user_role = payload.get("role", "user")
        user_info = {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": user_role
        }
        
        if user_role != required_role:
            from app.core.custom_exceptions import AuthorizationException
            raise AuthorizationException(f"Insufficient permissions: {required_role} role required")
        
        return user_info
    
    return role_checker
