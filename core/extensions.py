"""
Flask 扩展集中管理模块
所有 Flask 扩展在此初始化，避免循环导入问题
"""
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

# 初始化扩展（不绑定 app）
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def init_extensions(app):
    """
    初始化所有 Flask 扩展
    
    Args:
        app: Flask 应用实例
    """
    # CSRF 保护
    csrf.init_app(app)
    
    # 请求频率限制
    limiter.init_app(app)
    
    # CORS 配置（仅 API 路由）
    import config
    cors_config = {
        "origins": getattr(config, 'CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:8080']),
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False,
        "max_age": 3600
    }
    CORS(app, resources={r"/api/*": cors_config})
    
    return cors_config

