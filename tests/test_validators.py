"""
测试validators模块
"""
import pytest
from decimal import Decimal
from validators import (
    validate_username,
    validate_password,
    validate_email,
    validate_decimal,
    validate_string_length,
    validate_integer,
    validate_date_string,
    ValidationError
)


class TestValidateUsername:
    """测试用户名验证"""
    
    def test_valid_username(self):
        """测试有效用户名"""
        assert validate_username("testuser") == True
        assert validate_username("test_user_123") == True
        assert validate_username("abc") == True
    
    def test_username_too_short(self):
        """测试用户名过短"""
        with pytest.raises(ValidationError) as exc_info:
            validate_username("ab")
        assert "至少" in str(exc_info.value)
    
    def test_username_too_long(self):
        """测试用户名过长"""
        with pytest.raises(ValidationError) as exc_info:
            validate_username("a" * 51)
        assert "不能超过" in str(exc_info.value)
    
    def test_username_invalid_chars(self):
        """测试用户名包含非法字符"""
        with pytest.raises(ValidationError) as exc_info:
            validate_username("test-user")
        assert "只能包含" in str(exc_info.value)
    
    def test_username_empty(self):
        """测试空用户名"""
        with pytest.raises(ValidationError) as exc_info:
            validate_username("")
        assert "不能为空" in str(exc_info.value)


class TestValidatePassword:
    """测试密码验证"""
    
    def test_valid_password(self):
        """测试有效密码"""
        assert validate_password("password123") == True
        assert validate_password("123456") == True
    
    def test_password_too_short(self):
        """测试密码过短"""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("12345")
        assert "至少" in str(exc_info.value)
    
    def test_password_empty(self):
        """测试空密码"""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("")
        assert "不能为空" in str(exc_info.value)


class TestValidateEmail:
    """测试邮箱验证"""
    
    def test_valid_email(self):
        """测试有效邮箱"""
        assert validate_email("test@example.com") == True
        assert validate_email("user.name+tag@example.co.uk") == True
    
    def test_invalid_email(self):
        """测试无效邮箱"""
        with pytest.raises(ValidationError) as exc_info:
            validate_email("invalid.email")
        assert "格式不正确" in str(exc_info.value)
    
    def test_empty_email(self):
        """测试空邮箱（应该允许）"""
        assert validate_email("") == True
        assert validate_email(None) == True


class TestValidateDecimal:
    """测试小数验证"""
    
    def test_valid_decimal(self):
        """测试有效小数"""
        result = validate_decimal("10.5")
        assert result == Decimal("10.5")
        assert isinstance(result, Decimal)
    
    def test_decimal_with_range(self):
        """测试带范围的小数验证"""
        result = validate_decimal("5", min_value=0, max_value=10)
        assert result == Decimal("5")
    
    def test_decimal_below_min(self):
        """测试小于最小值"""
        with pytest.raises(ValidationError) as exc_info:
            validate_decimal("-1", min_value=0)
        assert "不能小于" in str(exc_info.value)
    
    def test_decimal_above_max(self):
        """测试大于最大值"""
        with pytest.raises(ValidationError) as exc_info:
            validate_decimal("11", max_value=10)
        assert "不能大于" in str(exc_info.value)
    
    def test_invalid_decimal(self):
        """测试无效小数"""
        with pytest.raises(ValidationError) as exc_info:
            validate_decimal("abc")
        assert "格式不正确" in str(exc_info.value)


class TestValidateInteger:
    """测试整数验证"""
    
    def test_valid_integer(self):
        """测试有效整数"""
        result = validate_integer("42")
        assert result == 42
        assert isinstance(result, int)
    
    def test_integer_with_range(self):
        """测试带范围的整数验证"""
        result = validate_integer("5", min_value=1, max_value=10)
        assert result == 5
    
    def test_integer_below_min(self):
        """测试小于最小值"""
        with pytest.raises(ValidationError) as exc_info:
            validate_integer("0", min_value=1)
        assert "不能小于" in str(exc_info.value)
    
    def test_invalid_integer(self):
        """测试无效整数"""
        with pytest.raises(ValidationError) as exc_info:
            validate_integer("abc")
        assert "必须是整数" in str(exc_info.value)


class TestValidateStringLength:
    """测试字符串长度验证"""
    
    def test_valid_string(self):
        """测试有效字符串"""
        result = validate_string_length("test", 10)
        assert result == "test"
    
    def test_string_too_long(self):
        """测试字符串过长"""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_length("a" * 11, 10)
        assert "不能超过" in str(exc_info.value)
    
    def test_empty_string_required(self):
        """测试必填字符串为空"""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_length("", 10, required=True)
        assert "不能为空" in str(exc_info.value)
    
    def test_empty_string_optional(self):
        """测试可选字符串为空"""
        result = validate_string_length("", 10, required=False)
        assert result == ""


class TestValidateDateString:
    """测试日期字符串验证"""
    
    def test_valid_date(self):
        """测试有效日期"""
        result = validate_date_string("2025-10-21")
        assert result == "2025-10-21"
    
    def test_invalid_date_format(self):
        """测试无效日期格式"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("21/10/2025")
        assert "格式不正确" in str(exc_info.value)
    
    def test_empty_date(self):
        """测试空日期"""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_string("")
        assert "不能为空" in str(exc_info.value)

