"""
生产环境配置文件
使用方法：export APP_CONFIG=config_production
"""
import os
from dotenv import load_dotenv

# 加载 .env.production 文件（生产环境专用）
load_dotenv('.env.production')

# 数据库连接配置（生产环境）
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'raise_on_warnings': True,
    # 生产环境额外配置
    'pool_name': 'mypool',
    'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),  # 连接池大小
    'pool_reset_session': True,
    'autocommit': False,
    'get_warnings': True,
}

# Flask配置
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
if not SECRET_KEY or SECRET_KEY == 'dev-secret-key-change-in-production':
    raise ValueError("生产环境必须设置强随机的 FLASK_SECRET_KEY!")

DEBUG = False  # 生产环境强制禁用Debug
TESTING = False
HOST = os.getenv('FLASK_HOST', '127.0.0.1')  # 生产环境建议使用127.0.0.1配合Nginx
PORT = int(os.getenv('FLASK_PORT', '5000'))
SESSION_LIFETIME = int(os.getenv('SESSION_LIFETIME', '28800'))

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # INFO, WARNING, ERROR
LOG_FILE_MAX_BYTES = int(os.getenv('LOG_FILE_MAX_BYTES', '10485760'))  # 10MB
LOG_FILE_BACKUP_COUNT = int(os.getenv('LOG_FILE_BACKUP_COUNT', '30'))  # 保留30个备份

# 频率限制配置（生产环境使用Redis）
RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'

# HTTPS配置
PREFERRED_URL_SCHEME = 'https'  # 生产环境使用HTTPS
SESSION_COOKIE_SECURE = True  # 要求HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CORS配置（如需要）
CORS_ENABLED = os.getenv('CORS_ENABLED', 'False').lower() == 'true'
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if CORS_ENABLED else []

# 性能配置
SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 静态文件缓存1年（秒）
JSON_SORT_KEYS = False  # 提升JSON序列化性能

# 安全配置
WTF_CSRF_TIME_LIMIT = None  # CSRF token不过期（直到session过期）
WTF_CSRF_SSL_STRICT = True  # HTTPS下严格CSRF检查
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传16MB

# 验证必要的环境变量
REQUIRED_ENV_VARS = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_DATABASE', 'FLASK_SECRET_KEY']
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"生产环境缺少必要的环境变量: {missing_vars}")

print(f"✓ 生产环境配置加载成功 - Database: {DB_CONFIG['host']}/{DB_CONFIG['database']}")

