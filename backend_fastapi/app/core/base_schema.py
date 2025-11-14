# -*- coding: utf-8 -*-
"""
基础Schema模块
提供通用的Pydantic模型基类
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """基础Schema"""
    model_config = ConfigDict(
        from_attributes=True,  # 允许从ORM模型创建
        use_enum_values=True,  # 使用枚举值
        validate_assignment=True,  # 赋值时验证
        str_strip_whitespace=True  # 去除字符串首尾空格
    )


class TimestampSchema(BaseSchema):
    """带时间戳的Schema"""
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")


class IDSchema(BaseSchema):
    """带ID的Schema"""
    id: int = Field(..., description="主键ID", gt=0)


class PaginationParams(BaseSchema):
    """分页参数"""
    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=20, description="每页数量", ge=1, le=5000)
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """获取限制数量"""
        return self.page_size

