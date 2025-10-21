"""
日志配置模块
提供统一的日志记录功能，替代 print 语句
"""
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(app=None):
    """
    配置应用日志系统
    
    Args:
        app: Flask应用实例（可选）
    
    Returns:
        logger: 配置好的logger实例
    """
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 设置日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # 文件处理器 - 记录所有日志
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 错误文件处理器 - 只记录错误
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    if app:
        # Flask应用日志
        app.logger.addHandler(file_handler)
        app.logger.addHandler(error_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.INFO)
        return app.logger
    else:
        # 通用日志
        logger = logging.getLogger(__name__)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        return logger


# 创建默认logger实例供其他模块使用
default_logger = setup_logger()

