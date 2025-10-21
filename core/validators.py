"""
输入验证模块
提供统一的输入验证功能
"""
import re
from decimal import Decimal, InvalidOperation
from .constants import (
    MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH,
    MAX_TRADE_NAME_LENGTH, MAX_SUPPLIER_LENGTH, MAX_PROJECT_NAME_LENGTH
)


class ValidationError(Exception):
    """验证错误异常"""
    pass


def validate_username(username):
    """
    验证用户名
    
    Args:
        username: 用户名字符串
    
    Returns:
        bool: 验证通过返回True
    
    Raises:
        ValidationError: 验证失败时抛出
    """
    if not username:
        raise ValidationError("用户名不能为空")
    
    if len(username) < MIN_USERNAME_LENGTH:
        raise ValidationError(f"用户名长度至少{MIN_USERNAME_LENGTH}个字符")
    
    if len(username) > MAX_USERNAME_LENGTH:
        raise ValidationError(f"用户名长度不能超过{MAX_USERNAME_LENGTH}个字符")
    
    # 只允许字母、数字、下划线
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("用户名只能包含字母、数字和下划线")
    
    return True


def validate_password(password):
    """
    验证密码强度
    
    Args:
        password: 密码字符串
    
    Returns:
        bool: 验证通过返回True
    
    Raises:
        ValidationError: 验证失败时抛出
    """
    if not password:
        raise ValidationError("密码不能为空")
    
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"密码长度至少{MIN_PASSWORD_LENGTH}个字符")
    
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValidationError(f"密码长度不能超过{MAX_PASSWORD_LENGTH}个字符")
    
    return True


def validate_email(email):
    """
    验证邮箱格式
    
    Args:
        email: 邮箱字符串
    
    Returns:
        bool: 验证通过返回True
    
    Raises:
        ValidationError: 验证失败时抛出
    """
    if not email:
        return True  # 邮箱是可选的
    
    # 简单的邮箱格式验证
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("邮箱格式不正确")
    
    return True


def validate_decimal(value, min_value=None, max_value=None, field_name="数值"):
    """
    验证小数值
    
    Args:
        value: 要验证的值
        min_value: 最小值（可选）
        max_value: 最大值（可选）
        field_name: 字段名称，用于错误消息
    
    Returns:
        Decimal: 验证后的Decimal对象
    
    Raises:
        ValidationError: 验证失败时抛出
    """
    if value is None or value == '':
        raise ValidationError(f"{field_name}不能为空")
    
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"{field_name}格式不正确")
    
    if min_value is not None and decimal_value < Decimal(str(min_value)):
        raise ValidationError(f"{field_name}不能小于{min_value}")
    
    if max_value is not None and decimal_value > Decimal(str(max_value)):
        raise ValidationError(f"{field_name}不能大于{max_value}")
    
    return decimal_value


def validate_string_length(value, max_length, field_name="字段", required=True):
    """
    验证字符串长度
    
    Args:
        value: 要验证的字符串
        max_length: 最大长度
        field_name: 字段名称
        required: 是否必填
    
    Returns:
        str: 验证后的字符串
    
    Raises:
        ValidationError: 验证失败时抛出
    """
    if not value or value.strip() == '':
        if required:
            raise ValidationError(f"{field_name}不能为空")
        return value
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name}长度不能超过{max_length}个字符")
    
    return value


def validate_integer(value, min_value=None, max_value=None, field_name="整数"):
    """
    验证整数值
    
    Args:
        value: 要验证的值
        min_value: 最小值（可选）
        max_value: 最大值（可选）
        field_name: 字段名称
    
    Returns:
        int: 验证后的整数
    
    Raises:
        ValidationError: 验证失败时抛出
    """
    if value is None or value == '':
        raise ValidationError(f"{field_name}不能为空")
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name}必须是整数")
    
    if min_value is not None and int_value < min_value:
        raise ValidationError(f"{field_name}不能小于{min_value}")
    
    if max_value is not None and int_value > max_value:
        raise ValidationError(f"{field_name}不能大于{max_value}")
    
    return int_value


def validate_date_string(date_str, field_name="日期"):
    """
    验证日期字符串格式 (YYYY-MM-DD)
    
    Args:
        date_str: 日期字符串
        field_name: 字段名称
    
    Returns:
        str: 验证后的日期字符串
    
    Raises:
        ValidationError: 验证失败时抛出
    """
    if not date_str:
        raise ValidationError(f"{field_name}不能为空")
    
    # 验证格式 YYYY-MM-DD
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise ValidationError(f"{field_name}格式不正确，应为 YYYY-MM-DD")
    
    return date_str

