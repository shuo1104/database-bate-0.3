"""
Flask 扩展集中管理模块
所有 Flask 扩展在此初始化，避免循环导入问题
"""
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

