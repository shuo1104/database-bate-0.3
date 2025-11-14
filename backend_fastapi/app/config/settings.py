# -*- coding: utf-8 -*-
"""
系统配置模块
使用Pydantic Settings管理配置
"""

import os
from typing import ClassVar, List, Literal
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """系统配置类"""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf-8",
        extra='ignore',
        case_sensitive=True
    )
    
    # Banner
    BANNER: ClassVar[str] = """
    ╔═══════════════════════════════════════════════════════════╗
    ║   Advanced - PhotoPolymer Formulation Management DB       ║                                         ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    
    # ==================== 环境配置 ====================
    ENVIRONMENT: str = "dev"  # dev, test, prod
    
    # ==================== 项目配置 ====================
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    
    # ==================== 服务器配置 ====================
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    RELOAD: bool = True  # 开发环境自动重载（与 WORKERS > 1 互斥）
    WORKERS: int = 1  # Uvicorn 工作进程数。生产环境建议：CPU核心数 × 2 + 1
    
    # ==================== API文档配置 ====================
    TITLE: str = "Advanced - PhotoPolymer Formulation Management API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "高级光敏聚合物配方管理数据库 RESTful API"
    SUMMARY: str = "基于 FastAPI 的现代化配方管理系统"
    DOCS_URL: str = "/docs"  # Swagger UI
    REDOC_URL: str = "/redoc"  # ReDoc
    DEBUG: bool = True
    
    # ==================== CORS配置 ====================
    CORS_ENABLE: bool = True
    ALLOW_ORIGINS: List[str] = [
        "http://localhost:3000",    # frontend_vue3 开发服务器
        "http://localhost:5173",    # Vite 默认端口
        "http://localhost:5180",    # 其他前端服务
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    
    # ==================== JWT认证配置 ====================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-only-for-development-DO-NOT-USE-IN-PRODUCTION")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    TOKEN_TYPE: str = "bearer"
    
    # JWT路由白名单（无需认证的接口）
    TOKEN_REQUEST_PATH_EXCLUDE: List[str] = [
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health"
    ]
    
    # ==================== 数据库配置 ====================
    # 数据库基础配置（优先使用环境变量）
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))  # PostgreSQL 默认端口
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    DB_DATABASE: str = os.getenv("DB_DATABASE", "photopolymer_formulation_db")
    
    # 数据库引擎配置
    DATABASE_ECHO: bool | Literal['debug'] = False  # SQL日志
    POOL_SIZE: int = 20  # 连接池大小
    MAX_OVERFLOW: int = 10  # 最大溢出连接
    POOL_TIMEOUT: int = 30  # 连接超时(秒)
    POOL_RECYCLE: int = 1800  # 连接回收时间(秒)
    POOL_PRE_PING: bool = True  # 连接预检
    
    # ==================== Redis配置 ====================
    REDIS_ENABLE: bool = False  # 是否启用Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: str = "app.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 10
    
    # ==================== 文件上传配置 ====================
    UPLOAD_DIR: Path = BASE_DIR / "static" / "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".xlsx", ".csv"]
    
    # ==================== 分页配置 ====================
    PAGE_SIZE_DEFAULT: int = 20
    PAGE_SIZE_OPTIONS: List[int] = [10, 20, 50, 100]
    
    # ==================== 动态属性 ====================
    @property
    def DB_URI(self) -> str:
        """同步数据库连接URI (PostgreSQL)"""
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
        )
    
    @property
    def ASYNC_DB_URI(self) -> str:
        """异步数据库连接URI (PostgreSQL)"""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
        )
    
    @property
    def REDIS_URI(self) -> str:
        """Redis连接URI"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# 根据环境加载不同配置
def get_settings() -> Settings:
    """获取配置实例"""
    env = os.getenv("ENVIRONMENT", "dev")
    env_file = Path(__file__).parent.parent.parent / "env" / f".env.{env}"
    
    if env_file.exists():
        return Settings(_env_file=str(env_file))
    return Settings()


# 全局配置实例
settings = get_settings()

