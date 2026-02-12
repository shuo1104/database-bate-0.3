# -*- coding: utf-8 -*-
"""
统一响应封装模块
"""

from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse


T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    success: bool = Field(default=True, description="是否成功")


class SuccessResponse(JSONResponse):
    """成功响应"""
    
    def __init__(
        self,
        data: Any = None,
        msg: str = "操作成功",
        code: int = 200,
        **kwargs
    ):
        content = {
            "code": code,
            "msg": msg,
            "data": data,
            "success": True
        }
        super().__init__(content=content, status_code=code, **kwargs)


class ErrorResponse(JSONResponse):
    """错误响应"""
    
    def __init__(
        self,
        msg: str = "操作失败",
        code: int = 400,
        data: Any = None,
        **kwargs
    ):
        content = {
            "code": code,
            "msg": msg,
            "data": data,
            "success": False
        }
        super().__init__(content=content, status_code=code, **kwargs)


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="响应消息")
    data: list[T] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=20, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")
    success: bool = Field(default=True, description="是否成功")

