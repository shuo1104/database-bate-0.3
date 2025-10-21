"""
配置模块
管理应用的各种配置
"""
import os

# 根据环境加载不同配置
env = os.getenv('APP_ENV', 'development')

if env == 'production':
    from .production import *
else:
    from .config import *

__all__ = [
    'DB_CONFIG',
    'SECRET_KEY',
    'DEBUG',
    'HOST',
    'PORT',
    'SESSION_LIFETIME',
    'CORS_ENABLED',
    'CORS_ORIGINS',
    'JWT_SECRET_KEY',
    'JWT_ACCESS_TOKEN_EXPIRES',
    'JWT_REFRESH_TOKEN_EXPIRES'
]

