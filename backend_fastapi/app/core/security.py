# -*- coding: utf-8 -*-
"""
安全认证模块
JWT令牌生成和验证、密码加密
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.settings import settings
from app.core.logger import logger


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
    验证密码（支持 Argon2、Bcrypt 和明文密码）
    
    Args:
        plain_password: 明文密码
        hashed_password: 密码哈希或明文密码
    
    Returns:
        密码是否匹配
    """
    # 如果数据库中存储的是明文密码（没有哈希前缀），直接比对
    # 哈希密码通常以 $ 开头，如 $2b$, $argon2id$ 等
    if not hashed_password.startswith('$'):
        logger.warning("检测到明文密码存储，建议使用哈希密码")
        return plain_password == hashed_password
    
    # 使用 passlib 验证哈希密码（自动识别 Argon2 或 Bcrypt）
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"密码哈希验证失败: {e}")
        # 如果哈希验证失败，尝试明文比对（兼容性处理）
        return plain_password == hashed_password


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
        logger.error(f"JWT解码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌：缺少用户信息",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要{required_role}角色"
            )
        
        return user_info
    
    return role_checker
