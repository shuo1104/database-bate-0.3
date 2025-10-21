import mysql.connector
from config import config
import decimal
import logging
from datetime import date, datetime

# 获取logger实例
logger = logging.getLogger(__name__)

def get_db_connection():
    """Establishes a connection to the MySQL database using config.DB_CONFIG."""
    try:
        cnx = mysql.connector.connect(**config.DB_CONFIG)
        return cnx
    except mysql.connector.Error as err:
        logger.error(f"数据库连接失败: {err}")
        return None

def make_json_safe(obj):
    """
    递归地将任何对象转换为JSON安全的原始类型。
    - decimal.Decimal -> str (保留精度)
    - datetime/date -> ISO 字符串
    - bytes -> utf-8 (备用方案 hex)
    - set/tuple -> list
    - dict/list 递归处理
    - 其他 -> str
    """
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [make_json_safe(v) for v in obj]
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8')
        except Exception:
            return obj.hex()
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    return str(obj)
