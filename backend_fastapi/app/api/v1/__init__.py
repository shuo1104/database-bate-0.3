# -*- coding: utf-8 -*-
"""
API v1 路由汇总
"""

from fastapi import APIRouter

# 创建API路由
api_router = APIRouter()

# 导入各模块路由
from app.api.v1.modules.auth.controller import router as auth_router
from app.api.v1.modules.projects.controller import router as projects_router
from app.api.v1.modules.materials.controller import router as materials_router
from app.api.v1.modules.fillers.controller import router as fillers_router
from app.api.v1.modules.test_results.controller import router as test_results_router
from app.api.v1.modules.logs.controller import router as logs_router

# 注册路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证管理"])
api_router.include_router(projects_router, prefix="/projects", tags=["项目管理"])
api_router.include_router(materials_router, prefix="/materials", tags=["原料管理"])
api_router.include_router(fillers_router, prefix="/fillers", tags=["填料管理"])
api_router.include_router(test_results_router, prefix="/test-results", tags=["测试结果管理"])
api_router.include_router(logs_router, tags=["系统日志"])

