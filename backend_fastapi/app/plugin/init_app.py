# -*- coding: utf-8 -*-
"""
应用初始化插件
注册中间件、异常处理器、路由等
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.middlewares import (
    register_cors,
    register_request_logger,
    register_auth_middleware
)
from app.core.exceptions import register_exception_handlers
from app.core.logger import logger
from app.config.settings import settings


def register_middlewares(app: FastAPI) -> None:
    """
    注册所有中间件
    
    Args:
        app: FastAPI应用实例
    """
    logger.info("🔧 开始注册中间件...")
    
    # CORS中间件
    register_cors(app)
    
    # 请求日志中间件
    register_request_logger(app)
    
    # 认证中间件（可选，根据需求启用）
    # register_auth_middleware(app)
    
    logger.info("✅ 所有中间件注册完成")


def register_exceptions(app: FastAPI) -> None:
    """
    注册全局异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    logger.info("🔧 开始注册异常处理器...")
    register_exception_handlers(app)
    logger.info("✅ 异常处理器注册完成")


def register_routers(app: FastAPI) -> None:
    """
    注册所有路由
    
    Args:
        app: FastAPI应用实例
    """
    logger.info("🔧 开始注册路由...")
    
    from app.api.v1 import api_router
    
    # 注册API v1路由
    app.include_router(
        api_router,
        prefix="/api/v1"
    )
    
    # 健康检查路由
    @app.get("/health", tags=["系统"])
    async def health_check():
        """健康检查接口"""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    logger.info("✅ 所有路由注册完成")


def register_static_files(app: FastAPI) -> None:
    """
    注册静态文件服务
    
    Args:
        app: FastAPI应用实例
    """
    logger.info("🔧 开始注册静态文件...")
    
    # 创建静态文件目录
    static_dir = settings.BASE_DIR / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # 挂载静态文件
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    logger.info("✅ 静态文件服务注册完成")

