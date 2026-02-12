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
    register_auth_middleware,
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
    logger.info("🔧 Registering middlewares...")

    # CORS中间件
    register_cors(app)

    # 请求日志中间件
    register_request_logger(app)

    # 认证中间件（可选，根据需求启用）
    if settings.AUTH_MIDDLEWARE_ENABLE:
        register_auth_middleware(app)

    logger.info("✅ All middlewares registered")


def register_exceptions(app: FastAPI) -> None:
    """
    注册全局异常处理器

    Args:
        app: FastAPI应用实例
    """
    logger.info("🔧 Registering exception handlers...")
    register_exception_handlers(app)
    logger.info("✅ Exception handlers registered")


def register_routers(app: FastAPI) -> None:
    """
    注册所有路由

    Args:
        app: FastAPI应用实例
    """
    logger.info("🔧 Registering routes...")

    from app.api.v1 import api_router

    # 注册API v1路由
    app.include_router(api_router, prefix="/api/v1")

    # 健康检查路由
    @app.get("/health", tags=["系统"])
    async def health_check():
        """健康检查接口"""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        }

    @app.on_event("startup")
    async def startup_agent_warmup() -> None:
        """Agent 启动预热：Schema Grounding 和鉴权白名单校验。"""
        excluded_agent_paths = [
            path
            for path in settings.TOKEN_REQUEST_PATH_EXCLUDE
            if "/api/v1/agent" in path
        ]
        if excluded_agent_paths:
            logger.warning(
                "Agent endpoints should not be excluded from JWT auth: %s",
                excluded_agent_paths,
            )

        if not settings.AGENT_SCHEMA_GROUNDING_PRELOAD:
            logger.info("Agent schema grounding preload disabled")
            return

        try:
            from app.agent.tools.sql.schema_grounding import (
                build_schema_grounding_snapshot,
            )

            snapshot = await build_schema_grounding_snapshot()
            logger.info(
                "Agent schema grounding preloaded: tables=%s, relationships=%s",
                len(snapshot.get("tables", [])),
                len(snapshot.get("relationships", [])),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Agent schema grounding preload failed: %s: %s",
                type(exc).__name__,
                exc,
            )

    logger.info("✅ All routes registered")


def register_static_files(app: FastAPI) -> None:
    """
    注册静态文件服务

    Args:
        app: FastAPI应用实例
    """
    logger.info("🔧 Registering static files...")

    # 创建静态文件目录
    static_dir = settings.BASE_DIR / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    # 挂载静态文件
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    logger.info("✅ Static file service registered")
