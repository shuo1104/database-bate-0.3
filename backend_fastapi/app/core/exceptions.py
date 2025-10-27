# -*- coding: utf-8 -*-
"""
异常处理模块
提供全局异常处理器
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.logger import logger


class CustomException(Exception):
    """自定义异常基类"""
    
    def __init__(self, msg: str, code: int = 400):
        self.msg = msg
        self.code = code
        super().__init__(msg)


def register_exception_handlers(app: FastAPI) -> None:
    """
    注册全局异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        """自定义异常处理"""
        logger.warning(f"⚠️ 自定义异常: {exc.msg}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "code": exc.code,
                "msg": exc.msg,
                "success": False
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        """请求参数验证异常处理"""
        errors = exc.errors()
        error_msg = "; ".join([
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
            for err in errors
        ])
        logger.warning(f"⚠️ 参数验证失败: {error_msg}")
        
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
                "msg": f"参数验证失败: {error_msg}",
                "success": False,
                "detail": error_msg,
                "errors": serializable_errors
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError
    ):
        """数据库异常处理"""
        logger.error(f"❌ 数据库错误: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "msg": "数据库操作失败",
                "success": False
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理"""
        logger.error(f"❌ 未捕获异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "msg": "服务器内部错误",
                "success": False
            }
        )
    
    logger.info("✅ 异常处理器已注册")

