# -*- coding: utf-8 -*-
"""
日志系统模块
提供统一的日志记录功能
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.config.settings import settings


def setup_logger(name: str = "fastapi_app") -> logging.Logger:
    """
    配置应用日志系统
    
    Args:
        name: logger名称
    
    Returns:
        配置好的logger实例
    """
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建日志目录
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器 - 记录所有日志
    file_handler = RotatingFileHandler(
        filename=settings.LOG_DIR / settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 错误文件处理器 - 只记录错误
    error_handler = RotatingFileHandler(
        filename=settings.LOG_DIR / "error.log",
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger


# 全局logger实例
logger = setup_logger()

