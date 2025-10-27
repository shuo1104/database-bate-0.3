# -*- coding: utf-8 -*-
"""
数据库核心模块
提供同步和异步数据库引擎
"""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from typing import AsyncGenerator

from app.config.settings import settings
from app.core.logger import logger


# ==================== 基础模型类 ====================
class Base(DeclarativeBase):
    """SQLAlchemy基础模型类"""
    pass


# ==================== 同步数据库引擎 ====================
# 用于Alembic迁移和同步操作
engine: Engine = create_engine(
    url=settings.DB_URI,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=settings.POOL_PRE_PING,
    pool_recycle=settings.POOL_RECYCLE,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_timeout=settings.POOL_TIMEOUT
)

# 同步会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==================== 异步数据库引擎 ====================
# 主要用于FastAPI异步操作
async_engine: AsyncEngine = create_async_engine(
    url=settings.ASYNC_DB_URI,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=settings.POOL_PRE_PING,
    pool_recycle=settings.POOL_RECYCLE,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_timeout=settings.POOL_TIMEOUT,
    future=True
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


# ==================== 依赖注入函数 ====================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话
    用于FastAPI依赖注入
    
    示例:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ==================== 数据库初始化 ====================
async def init_database():
    """初始化数据库表"""
    try:
        async with async_engine.begin() as conn:
            # 创建所有表（生产环境应使用Alembic迁移）
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ 数据库表初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库表初始化失败: {e}")
        raise


async def close_database():
    """关闭数据库连接"""
    await async_engine.dispose()
    logger.info("✅ 数据库连接已关闭")

