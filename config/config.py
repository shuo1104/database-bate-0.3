"""
配置文件 - 使用环境变量来保护敏感信息
请复制 env.example 为 .env 并填写实际配置
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 数据库连接配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),  # 默认值仅用于开发环境
    'database': os.getenv('DB_DATABASE', 'test_base'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
    # 注意: 如果MySQL版本较老(< 5.5.3)，使用 utf8_general_ci
    # 'collation': 'utf8mb4_unicode_ci',  # 注释掉以使用默认值
    'raise_on_warnings': False  # 改为False避免警告导致连接失败
}

# Flask配置
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', '5000'))
SESSION_LIFETIME = int(os.getenv('SESSION_LIFETIME', '28800'))
