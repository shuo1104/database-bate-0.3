"""
测试utils模块
"""
import pytest
from decimal import Decimal
from datetime import datetime, date
from utils import make_json_safe


class TestMakeJsonSafe:
    """测试make_json_safe函数"""
    
    def test_basic_types(self):
        """测试基本类型"""
        assert make_json_safe(None) is None
        assert make_json_safe(True) is True
        assert make_json_safe(False) is False
        assert make_json_safe(42) == 42
        assert make_json_safe(3.14) == 3.14
        assert make_json_safe("string") == "string"
    
    def test_decimal_conversion(self):
        """测试Decimal转换"""
        result = make_json_safe(Decimal("10.5"))
        assert result == "10.5"
        assert isinstance(result, str)
    
    def test_datetime_conversion(self):
        """测试日期时间转换"""
        dt = datetime(2025, 10, 21, 10, 30, 0)
        result = make_json_safe(dt)
        assert result == "2025-10-21T10:30:00"
        assert isinstance(result, str)
        
        d = date(2025, 10, 21)
        result = make_json_safe(d)
        assert result == "2025-10-21"
        assert isinstance(result, str)
    
    def test_bytes_conversion(self):
        """测试bytes转换"""
        result = make_json_safe(b"hello")
        assert result == "hello"
        assert isinstance(result, str)
    
    def test_list_conversion(self):
        """测试列表转换"""
        result = make_json_safe([1, Decimal("2.5"), "3"])
        assert result == [1, "2.5", "3"]
    
    def test_dict_conversion(self):
        """测试字典转换"""
        result = make_json_safe({
            "decimal": Decimal("10.5"),
            "date": date(2025, 10, 21),
            "string": "test",
            "number": 42
        })
        assert result == {
            "decimal": "10.5",
            "date": "2025-10-21",
            "string": "test",
            "number": 42
        }
    
    def test_nested_structures(self):
        """测试嵌套结构"""
        result = make_json_safe({
            "list": [Decimal("1.5"), Decimal("2.5")],
            "dict": {
                "nested": Decimal("3.5")
            }
        })
        assert result == {
            "list": ["1.5", "2.5"],
            "dict": {
                "nested": "3.5"
            }
        }
    
    def test_tuple_and_set_conversion(self):
        """测试tuple和set转换"""
        result = make_json_safe((1, 2, 3))
        assert result == [1, 2, 3]
        
        result = make_json_safe({1, 2, 3})
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}

