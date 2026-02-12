# -*- coding: utf-8 -*-
"""
系统配置模块
使用Pydantic Settings管理配置
"""

import json
import os
from typing import ClassVar, List, Literal
from urllib.parse import urlparse
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """系统配置类"""

    DEFAULT_SECRET_KEY: ClassVar[str] = (
        "dev-secret-key-only-for-development-DO-NOT-USE-IN-PRODUCTION"
    )
    INSECURE_DB_PASSWORDS: ClassVar[set[str]] = {"", "root", "postgres", "password"}

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
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
    API_BASE_URL: str | None = None
    RELOAD: bool = False  # 开发环境自动重载（与 WORKERS > 1 互斥）
    WORKERS: int = 1  # Uvicorn 工作进程数。生产环境建议：CPU核心数 × 2 + 1

    # ==================== API文档配置 ====================
    TITLE: str = "Advanced - PhotoPolymer Formulation Management API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "高级光敏聚合物配方管理数据库 RESTful API"
    SUMMARY: str = "基于 FastAPI 的现代化配方管理系统"
    DOCS_URL: str = "/docs"  # Swagger UI
    REDOC_URL: str = "/redoc"  # ReDoc
    DEBUG: bool = False

    # ==================== CORS配置 ====================
    CORS_ENABLE: bool = True
    ALLOW_ORIGINS: List[str] = [
        "http://localhost:3000",  # frontend_vue3 开发服务器
        "http://localhost:5173",  # Vite 默认端口
        "http://localhost:5180",  # 其他前端服务
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://192.168.112.44:8080",  # 公网访问 - 请替换 YOUR_PUBLIC_IP 为实际公网IP
        "http://192.168.112.44",  # 公网访问（80端口）
    ]
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True

    # ==================== JWT认证配置 ====================
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
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
        "/api/v1/openapi.json",
        "/health",
    ]

    # ==================== 数据库配置 ====================
    # 数据库基础配置（优先使用环境变量）
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))  # PostgreSQL 默认端口
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_DATABASE: str = os.getenv("DB_DATABASE", "photopolymer_formulation_db")

    # 数据库引擎配置
    DATABASE_ECHO: bool | Literal["debug"] = False  # SQL日志
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
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".pdf",
        ".xlsx",
        ".csv",
    ]

    # ==================== 分页配置 ====================
    PAGE_SIZE_DEFAULT: int = 20
    PAGE_SIZE_OPTIONS: List[int] = [10, 20, 50, 100]

    # ==================== 认证中间件配置 ====================
    AUTH_MIDDLEWARE_ENABLE: bool = False

    # ==================== 速率限制配置 ====================
    RATE_LIMIT_ENABLE: bool = True
    RATE_LIMIT_LOGIN_MAX: int = 10
    RATE_LIMIT_LOGIN_WINDOW_SECONDS: int = 300
    RATE_LIMIT_REGISTER_MAX: int = 5
    RATE_LIMIT_REGISTER_WINDOW_SECONDS: int = 3600

    # ==================== Agent 配置 ====================
    # Deepseek (OpenAI-compatible) — 优先使用环境变量
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv(
        "DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"
    )
    # deepseek-chat/deepseek-reasoner are currently DeepSeek-V3.2 aliases
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # Agent LLM 参数
    AGENT_LLM_TEMPERATURE: float = float(os.getenv("AGENT_LLM_TEMPERATURE", "0.2"))
    AGENT_LLM_MAX_TOKENS: int = int(os.getenv("AGENT_LLM_MAX_TOKENS", "2048"))

    # MinerU API
    MINERU_API_URL: str = os.getenv("MINERU_API_URL", "http://localhost:8001")
    MINERU_API_KEY: str = os.getenv("MINERU_API_KEY", "")
    MINERU_PARSE_PATH: str = os.getenv("MINERU_PARSE_PATH", "/parse")
    MINERU_API_TIMEOUT: int = int(os.getenv("MINERU_API_TIMEOUT", "30"))

    # Agent ingest pipeline
    AGENT_UPLOAD_DIR: Path = Path(
        os.getenv("AGENT_UPLOAD_DIR", str(BASE_DIR / "static" / "uploads" / "agent"))
    )
    AGENT_MAX_FILE_SIZE: int = int(
        os.getenv("AGENT_MAX_FILE_SIZE", str(20 * 1024 * 1024))
    )
    AGENT_ALLOWED_EXTENSIONS: List[str] = [
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".csv",
    ]
    AGENT_REVIEW_CONFIDENCE_THRESHOLD: float = float(
        os.getenv("AGENT_REVIEW_CONFIDENCE_THRESHOLD", "0.75")
    )
    AGENT_ALLOWED_ROLES: List[str] = json.loads(
        os.getenv("AGENT_ALLOWED_ROLES", '["admin", "user"]')
    )
    AGENT_REVIEW_ROLES: List[str] = json.loads(
        os.getenv("AGENT_REVIEW_ROLES", '["admin"]')
    )
    AGENT_ENFORCE_PROJECT_SCOPE_ROLES: List[str] = json.loads(
        os.getenv("AGENT_ENFORCE_PROJECT_SCOPE_ROLES", '["user"]')
    )
    AGENT_MUTATION_ROLES: List[str] = json.loads(
        os.getenv("AGENT_MUTATION_ROLES", '["admin"]')
    )
    AGENT_ADMIN_ROLES: List[str] = json.loads(
        os.getenv("AGENT_ADMIN_ROLES", '["superadmin"]')
    )
    AGENT_SCHEMA_GROUNDING_PRELOAD: bool = os.getenv(
        "AGENT_SCHEMA_GROUNDING_PRELOAD", "true"
    ).lower() in {"1", "true", "yes", "on"}
    AGENT_REACT_RECURSION_LIMIT: int = int(
        os.getenv("AGENT_REACT_RECURSION_LIMIT", "12")
    )
    AGENT_MUTATION_REQUIRE_CONFIRMATION: bool = os.getenv(
        "AGENT_MUTATION_REQUIRE_CONFIRMATION", "true"
    ).lower() in {"1", "true", "yes", "on"}
    AGENT_MUTATION_MAX_BATCH_SIZE: int = int(
        os.getenv("AGENT_MUTATION_MAX_BATCH_SIZE", "100")
    )

    # Text-to-SQL 安全策略
    AGENT_SQL_TIMEOUT: int = int(os.getenv("AGENT_SQL_TIMEOUT", "10"))
    AGENT_SQL_MAX_RETRIES: int = int(os.getenv("AGENT_SQL_MAX_RETRIES", "2"))
    AGENT_SQL_ALLOWLIST_TABLES: List[str] = json.loads(
        os.getenv("AGENT_SQL_ALLOWLIST_TABLES", "[]")
    ) or [
        "tbl_ProjectInfo",
        "tbl_FormulaComposition",
        "tbl_RawMaterials",
        "tbl_InorganicFillers",
        "tbl_TestResults_Ink",
        "tbl_TestResults_Coating",
        "tbl_TestResults_3DPrint",
        "tbl_TestResults_Composite",
    ]

    # Text-to-SQL 只读连接（agent_readonly）
    AGENT_DB_READONLY_HOST: str = os.getenv("AGENT_DB_READONLY_HOST", DB_HOST)
    AGENT_DB_READONLY_PORT: int = int(os.getenv("AGENT_DB_READONLY_PORT", str(DB_PORT)))
    AGENT_DB_READONLY_USER: str = os.getenv("AGENT_DB_READONLY_USER", "agent_readonly")
    AGENT_DB_READONLY_PASSWORD: str = os.getenv(
        "AGENT_DB_READONLY_PASSWORD", DB_PASSWORD
    )
    AGENT_DB_READONLY_DATABASE: str = os.getenv(
        "AGENT_DB_READONLY_DATABASE", DB_DATABASE
    )

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
    def AGENT_READONLY_ASYNC_DB_URI(self) -> str:
        """Agent Text-to-SQL 只读连接URI。"""
        return (
            "postgresql+asyncpg://"
            f"{self.AGENT_DB_READONLY_USER}:{self.AGENT_DB_READONLY_PASSWORD}"
            f"@{self.AGENT_DB_READONLY_HOST}:{self.AGENT_DB_READONLY_PORT}"
            f"/{self.AGENT_DB_READONLY_DATABASE}"
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
    env = os.getenv("ENVIRONMENT", "dev").lower()
    env_file = Path(__file__).parent.parent.parent / "env" / f".env.{env}"
    shared_env_file = Path(__file__).parent.parent.parent.parent / ".env"

    env_files: list[str] = []
    if shared_env_file.exists():
        env_files.append(str(shared_env_file))
    if env_file.exists():
        env_files.append(str(env_file))

    for env_path in env_files:
        load_dotenv(env_path, override=False)

    settings = Settings()

    fields_set = getattr(settings, "model_fields_set", set())

    if settings.API_BASE_URL:
        use_api_base = env in {"dev", "development", "test"} or (
            "SERVER_HOST" not in fields_set or "SERVER_PORT" not in fields_set
        )
        if use_api_base:
            parsed_url = urlparse(settings.API_BASE_URL)
            if parsed_url.hostname:
                settings.SERVER_HOST = parsed_url.hostname
            if parsed_url.port:
                settings.SERVER_PORT = parsed_url.port
            elif parsed_url.scheme == "https":
                settings.SERVER_PORT = 443
            elif parsed_url.scheme == "http":
                settings.SERVER_PORT = 80

    if env in {"dev", "development", "test"}:
        if "DEBUG" not in fields_set:
            settings.DEBUG = True
        if "RELOAD" not in fields_set:
            settings.RELOAD = True
    else:
        settings.DEBUG = False
        settings.RELOAD = False

    if env in {"prod", "production"}:
        if (
            settings.SECRET_KEY == settings.DEFAULT_SECRET_KEY
            or len(settings.SECRET_KEY) < 32
        ):
            raise RuntimeError(
                "SECRET_KEY must be set to a secure random value in production"
            )
        if settings.DB_PASSWORD in settings.INSECURE_DB_PASSWORDS:
            raise RuntimeError(
                "DB_PASSWORD must be set to a secure value in production"
            )
        settings.AUTH_MIDDLEWARE_ENABLE = True

    return settings


# 全局配置实例
settings = get_settings()
