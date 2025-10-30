# -*- coding: utf-8 -*-
"""
自定义异常类
提供更细粒度的异常处理，便于错误追踪和处理
"""

from typing import Any, Optional
from fastapi import status


class BaseAPIException(Exception):
    """API异常基类"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


# ==================== 数据库相关异常 ====================
class DatabaseException(BaseAPIException):
    """数据库操作异常"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class RecordNotFoundException(BaseAPIException):
    """记录未找到异常"""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier}
        )


class DuplicateRecordException(BaseAPIException):
    """记录重复异常"""
    
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field}='{value}' already exists",
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": resource, "field": field, "value": value}
        )


class IntegrityConstraintException(BaseAPIException):
    """数据完整性约束异常"""
    
    def __init__(self, message: str = "Data integrity constraint violated", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


# ==================== 业务逻辑相关异常 ====================
class BusinessLogicException(BaseAPIException):
    """业务逻辑异常"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class ValidationException(BaseAPIException):
    """数据验证异常"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"field": field, "details": details} if field else details
        )


class InvalidOperationException(BaseAPIException):
    """无效操作异常"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


# ==================== 认证和授权相关异常 ====================
class AuthenticationException(BaseAPIException):
    """认证异常"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(BaseAPIException):
    """授权异常（权限不足）"""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class TokenExpiredException(AuthenticationException):
    """Token过期异常"""
    
    def __init__(self):
        super().__init__(message="Token has expired")


class InvalidTokenException(AuthenticationException):
    """无效Token异常"""
    
    def __init__(self):
        super().__init__(message="Invalid token")


# ==================== 外部服务相关异常 ====================
class ExternalServiceException(BaseAPIException):
    """外部服务异常"""
    
    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service_name}
        )


# ==================== 文件操作相关异常 ====================
class FileOperationException(BaseAPIException):
    """文件操作异常"""
    
    def __init__(self, operation: str, filename: str, reason: Optional[str] = None):
        message = f"File {operation} failed for '{filename}'"
        if reason:
            message += f": {reason}"
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"operation": operation, "filename": filename, "reason": reason}
        )


class FileNotFoundError(BaseAPIException):
    """文件未找到异常"""
    
    def __init__(self, filename: str):
        super().__init__(
            message=f"File '{filename}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"filename": filename}
        )


# ==================== 配置相关异常 ====================
class ConfigurationException(BaseAPIException):
    """配置异常"""
    
    def __init__(self, config_key: str, message: str = "Configuration error"):
        super().__init__(
            message=f"{message}: {config_key}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"config_key": config_key}
        )


# ==================== 辅助函数 ====================
def get_safe_error_message(exception: Exception, default_message: str = "An error occurred") -> str:
    """
    获取安全的错误消息（不泄露敏感信息）
    
    Args:
        exception: 异常对象
        default_message: 默认消息
    
    Returns:
        安全的错误消息
    """
    if isinstance(exception, BaseAPIException):
        return exception.message
    
    # 对于系统异常，返回通用消息，不泄露细节
    return default_message

