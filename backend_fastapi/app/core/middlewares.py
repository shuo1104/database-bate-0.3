# -*- coding: utf-8 -*-
"""
中间件模块
提供CORS、日志、认证等中间件
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from app.config.settings import settings
from app.core.logger import logger


def register_cors(app: FastAPI) -> None:
    """
    注册CORS中间件
    
    Args:
        app: FastAPI应用实例
    """
    if settings.CORS_ENABLE:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOW_ORIGINS,
            allow_credentials=settings.ALLOW_CREDENTIALS,
            allow_methods=settings.ALLOW_METHODS,
            allow_headers=settings.ALLOW_HEADERS,
            expose_headers=["X-Request-ID"]
        )
        logger.info("✅ CORS middleware registered")


def register_request_logger(app: FastAPI) -> None:
    """
    注册请求日志中间件
    记录每个请求的耗时和状态
    
    Args:
        app: FastAPI应用实例
    """
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """记录请求日志"""
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"📥 {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 计算耗时
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # 记录响应信息
        logger.info(
            f"📤 {request.method} {request.url.path} "
            f"[{response.status_code}] {process_time:.3f}s"
        )
        
        return response
    
    logger.info("✅ Request logging middleware registered")


def register_auth_middleware(app: FastAPI) -> None:
    """
    注册认证中间件
    验证JWT令牌（路由白名单除外）
    
    Args:
        app: FastAPI应用实例
    """
    @app.middleware("http")
    async def authenticate_request(request: Request, call_next):
        """验证请求认证"""
        path = request.url.path
        
        # 检查是否在白名单中
        is_excluded = any(
            excluded_path in path
            for excluded_path in settings.TOKEN_REQUEST_PATH_EXCLUDE
        )
        
        if is_excluded:
            # 白名单路径，直接放行
            response = await call_next(request)
            return response
        
        # 验证Authorization头
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "code": 401,
                    "msg": "未提供认证令牌",
                    "success": False
                }
            )
        
        # 继续处理请求（令牌验证在依赖注入中进行）
        response = await call_next(request)
        return response
    
    logger.info("✅ Authentication middleware registered")

