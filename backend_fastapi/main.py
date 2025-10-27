# -*- coding: utf-8 -*-
"""
光创化物 R&D 数据库管理系统 - FastAPI版本
主启动文件
"""

import os
import uvicorn
import typer
from fastapi import FastAPI
from contextlib import asynccontextmanager

shell_app = typer.Typer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    from app.core.logger import logger
    from app.core.database import async_engine
    from app.config.settings import settings
    
    # 启动时初始化
    logger.info("=" * 80)
    logger.info(settings.BANNER)
    logger.info("=" * 80)
    logger.info(f"🚀 应用启动中... 环境: {settings.ENVIRONMENT}")
    logger.info(f"📖 API文档: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}{settings.DOCS_URL}")
    logger.info(f"📖 ReDoc文档: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}{settings.REDOC_URL}")
    
    yield
    
    # 关闭时清理
    logger.info("👋 应用正在关闭...")
    await async_engine.dispose()
    logger.info("✅ 数据库连接已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    from app.config.settings import settings
    from app.plugin.init_app import (
        register_middlewares,
        register_exceptions,
        register_routers,
        register_static_files
    )
    
    # 创建FastAPI实例
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        summary=settings.SUMMARY,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan
    )
    
    # 注册异常处理器
    register_exceptions(app)
    
    # 注册中间件
    register_middlewares(app)
    
    # 注册路由
    register_routers(app)
    
    # 注册静态文件
    register_static_files(app)
    
    return app


@shell_app.command()
def run(
    env: str = typer.Option("dev", "--env", help="运行环境 (dev, prod)")
):
    """启动应用服务"""
    typer.echo(f"[START] Project starting... Environment: {env}")
    
    # 设置环境变量
    os.environ["ENVIRONMENT"] = env
    
    # 确保在设置环境变量后导入配置
    from app.config.settings import settings
    
    # 启动uvicorn服务
    uvicorn.run(
        app="main:create_app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD,
        factory=True,
        log_level="info"
    )


if __name__ == '__main__':
    # 启动服务
    # python main.py run --env=dev
    shell_app()

