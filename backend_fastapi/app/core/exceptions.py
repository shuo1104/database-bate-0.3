# -*- coding: utf-8 -*-
"""
异常处理模块
提供全局异常处理器
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    DataError,
    OperationalError,
    DatabaseError
)
from psycopg2.errors import UniqueViolation, ForeignKeyViolation

from app.core.logger import logger
from app.core.custom_exceptions import (
    BaseAPIException,
    DatabaseException,
    RecordNotFoundException,
    DuplicateRecordException,
    IntegrityConstraintException,
    AuthenticationException,
    AuthorizationException,
    ValidationException,
    BusinessLogicException,
    ExternalServiceException,
    FileOperationException,
    get_safe_error_message
)


class CustomException(Exception):
    """
    自定义异常基类（已废弃，保留用于向后兼容）
    请使用 app.core.custom_exceptions 中的异常类
    """
    
    def __init__(self, msg: str, code: int = 400):
        self.msg = msg
        self.code = code
        super().__init__(msg)


def register_exception_handlers(app: FastAPI) -> None:
    """
    注册全局异常处理器
    
    异常处理优先级（从高到低）：
    1. 自定义业务异常（BaseAPIException及其子类）
    2. FastAPI验证异常（RequestValidationError）
    3. SQLAlchemy数据库异常（IntegrityError, DataError等）
    4. 通用数据库异常（SQLAlchemyError）
    5. 兜底全局异常（Exception）
    
    Args:
        app: FastAPI应用实例
    """
    
    # ==================== 1. 自定义业务异常处理 ====================
    @app.exception_handler(BaseAPIException)
    async def base_api_exception_handler(request: Request, exc: BaseAPIException):
        """
        处理所有自定义业务异常
        这些异常通常包含安全的、可直接返回给前端的错误信息
        """
        # 根据状态码选择日志级别
        if exc.status_code >= 500:
            logger.error(
                f"❌ Server Error [{exc.status_code}]: {exc.message}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "details": exc.details
                }
            )
        elif exc.status_code >= 400:
            logger.warning(
                f"⚠️ Client Error [{exc.status_code}]: {exc.message}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "details": exc.details
                }
            )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "msg": exc.message,
                "success": False,
                "details": exc.details
            }
        )
    
    # ==================== 2. FastAPI参数验证异常 ====================
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        """
        请求参数验证异常处理
        对Pydantic验证错误进行结构化处理
        """
        errors = exc.errors()
        error_msg = "; ".join([
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
            for err in errors
        ])
        logger.warning(
            f"⚠️ Validation Error: {error_msg}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": errors
            }
        )
        
        # 将错误信息转换为可JSON序列化的格式
        serializable_errors = []
        for err in errors:
            serializable_errors.append({
                "loc": list(err.get("loc", [])),
                "msg": str(err.get("msg", "")),
                "type": str(err.get("type", ""))
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 422,
                "msg": f"Validation failed: {error_msg}",
                "success": False,
                "errors": serializable_errors
            }
        )
    
    # ==================== 3. SQLAlchemy特定异常 ====================
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """
        数据完整性约束异常
        处理唯一约束、外键约束等违规
        """
        error_info = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        # 判断具体的完整性错误类型
        if isinstance(exc.orig, UniqueViolation):
            logger.warning(
                f"⚠️ Unique Constraint Violation: {error_info}",
                extra={"path": request.url.path, "method": request.method}
            )
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "code": 409,
                    "msg": "Record already exists (unique constraint violation)",
                    "success": False
                }
            )
        elif isinstance(exc.orig, ForeignKeyViolation):
            logger.warning(
                f"⚠️ Foreign Key Constraint Violation: {error_info}",
                extra={"path": request.url.path, "method": request.method}
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "code": 400,
                    "msg": "Referenced record does not exist (foreign key constraint violation)",
                    "success": False
                }
            )
        else:
            logger.error(
                f"❌ Data Integrity Error: {error_info}",
                extra={"path": request.url.path, "method": request.method},
                exc_info=True
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "code": 400,
                    "msg": "Data integrity constraint violated",
                    "success": False
                }
            )
    
    @app.exception_handler(DataError)
    async def data_error_handler(request: Request, exc: DataError):
        """
        数据类型错误
        例如：数据类型不匹配、数值超出范围等
        """
        logger.warning(
            f"⚠️ Data Error: {str(exc)}",
            extra={"path": request.url.path, "method": request.method}
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": 400,
                "msg": "Invalid data format or type",
                "success": False
            }
        )
    
    @app.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, exc: OperationalError):
        """
        数据库操作错误
        例如：连接失败、超时等
        """
        logger.error(
            f"❌ Database Operational Error: {str(exc)}",
            extra={"path": request.url.path, "method": request.method},
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "code": 503,
                "msg": "Database service temporarily unavailable",
                "success": False
            }
        )
    
    # ==================== 4. SQLAlchemy通用异常 ====================
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError
    ):
        """
        数据库异常处理（兜底）
        捕获所有未被上述特定处理器捕获的SQLAlchemy异常
        """
        logger.error(
            f"❌ Database Error: {str(exc)}",
            extra={"path": request.url.path, "method": request.method},
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "msg": "Database operation failed",
                "success": False
            }
        )
    
    # ==================== 5. 兼容旧版CustomException ====================
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        """
        自定义异常处理（向后兼容）
        新代码请使用 BaseAPIException 及其子类
        """
        logger.warning(
            f"⚠️ Legacy Custom Exception: {exc.msg}",
            extra={"path": request.url.path, "method": request.method}
        )
        return JSONResponse(
            status_code=exc.code,
            content={
                "code": exc.code,
                "msg": exc.msg,
                "success": False
            }
        )
    
    # ==================== 6. 全局兜底异常处理 ====================
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        全局异常处理（最后兜底）
        捕获所有未被上述处理器捕获的异常
        
        安全原则：不向前端暴露系统内部错误细节
        """
        logger.error(
            f"❌ Unhandled Exception: {type(exc).__name__}: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__
            },
            exc_info=True
        )
        
        # 返回通用错误消息，不泄露内部细节
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "msg": "Internal server error",
                "success": False
            }
        )
    
    logger.info("✅ Exception handlers registered successfully")

