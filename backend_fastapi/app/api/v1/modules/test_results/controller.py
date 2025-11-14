# -*- coding: utf-8 -*-
"""
测试结果管理Controller
"""

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.common.response import SuccessResponse
from app.api.v1.modules.test_results.service import TestResultService
from app.api.v1.modules.test_results.schema import (
    TestResultInkRequest,
    TestResultCoatingRequest,
    TestResult3DPrintRequest,
    TestResultCompositeRequest
)


router = APIRouter()


@router.get(
    "/project/{project_id}",
    response_model=None,
    summary="获取项目测试结果",
    description="根据项目ID获取测试结果，自动判断项目类型"
)
async def get_test_result(
    project_id: int = Path(..., gt=0, description="项目ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取测试结果"""
    result = await TestResultService.get_test_result(db, project_id)
    
    if result:
        return SuccessResponse(
            data=result.model_dump(mode='json'),
            msg="查询成功"
        )
    else:
        return SuccessResponse(
            data=None,
            msg="暂无测试结果"
        )


@router.post(
    "/ink/{project_id}",
    response_model=None,
    summary="创建或更新喷墨测试结果",
    description="为喷墨项目创建或更新测试结果"
)
async def create_or_update_ink_result(
    project_id: int = Path(..., gt=0, description="项目ID"),
    test_data: TestResultInkRequest = ...,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建或更新喷墨测试结果"""
    result = await TestResultService.create_or_update_ink_result(db, project_id, test_data)
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="操作成功"
    )


@router.post(
    "/coating/{project_id}",
    response_model=None,
    summary="创建或更新涂层测试结果",
    description="为涂层项目创建或更新测试结果"
)
async def create_or_update_coating_result(
    project_id: int = Path(..., gt=0, description="项目ID"),
    test_data: TestResultCoatingRequest = ...,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建或更新涂层测试结果"""
    result = await TestResultService.create_or_update_coating_result(db, project_id, test_data)
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="操作成功"
    )


@router.post(
    "/3dprint/{project_id}",
    response_model=None,
    summary="创建或更新3D打印测试结果",
    description="为3D打印项目创建或更新测试结果"
)
async def create_or_update_3dprint_result(
    project_id: int = Path(..., gt=0, description="项目ID"),
    test_data: TestResult3DPrintRequest = ...,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建或更新3D打印测试结果"""
    result = await TestResultService.create_or_update_3dprint_result(db, project_id, test_data)
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="操作成功"
    )


@router.post(
    "/composite/{project_id}",
    response_model=None,
    summary="创建或更新复合材料测试结果",
    description="为复合材料项目创建或更新测试结果"
)
async def create_or_update_composite_result(
    project_id: int = Path(..., gt=0, description="项目ID"),
    test_data: TestResultCompositeRequest = ...,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建或更新复合材料测试结果"""
    result = await TestResultService.create_or_update_composite_result(db, project_id, test_data)
    return SuccessResponse(
        data=result.model_dump(mode='json'),
        msg="操作成功"
    )

