# -*- coding: utf-8 -*-
"""
原料管理Controller
"""

from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.common.response import SuccessResponse
from app.utils.export_helper import ExportHelper
from app.api.v1.modules.materials.service import MaterialService
from app.api.v1.modules.materials.schema import (
    MaterialCreateRequest,
    MaterialUpdateRequest,
    MaterialQueryParams,
    MaterialResponse,
    MaterialCategoryResponse,
    BatchDeleteRequest
)


# 创建路由
router = APIRouter()


@router.get(
    "/list",
    response_model=None,
    summary="获取原料列表",
    description="分页查询原料列表，支持多条件筛选"
)
async def get_material_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: str = Query(None, description="原料类别"),
    supplier: str = Query(None, description="供应商"),
    keyword: str = Query(None, description="关键词搜索"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取原料列表（分页）
    
    需要认证: 是
    """
    query_params = MaterialQueryParams(
        category=category,
        supplier=supplier,
        keyword=keyword
    )
    
    materials, total = await MaterialService.get_material_list(
        db=db,
        page=page,
        page_size=page_size,
        query_params=query_params
    )
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    return SuccessResponse(
        data={
            "list": [m.model_dump(mode='json') for m in materials],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        },
        msg="查询成功"
    )


@router.get(
    "/export",
    response_model=None,
    summary="导出原料列表",
    description="导出原料列表数据为CSV或TXT格式"
)
async def export_materials(
    format: str = Query('csv', description="导出格式: csv 或 txt"),
    category: str = Query(None, description="类别"),
    supplier: str = Query(None, description="供应商"),
    keyword: str = Query(None, description="关键词"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """导出原料列表"""
    query_params = MaterialQueryParams(
        category=category,
        supplier=supplier,
        keyword=keyword
    )
    
    # 获取所有符合条件的原料
    materials, _ = await MaterialService.get_material_list(
        db=db,
        page=1,
        page_size=10000,
        query_params=query_params
    )
    
    # 定义列映射
    column_mapping = {
        'MaterialID': '原料ID',
        'TradeName': '商品名称',
        'CategoryName': '类别',
        'Supplier': '供应商',
        'CAS_Number': 'CAS号',
        'Density': '密度',
        'Viscosity': '粘度',
        'FunctionDescription': '功能说明',
    }
    
    # 准备导出数据
    export_data = ExportHelper.prepare_export_data(materials, column_mapping)
    
    # 导出
    content, filename = ExportHelper.export(
        data=export_data,
        columns=list(column_mapping.values()),
        format=format,
        filename=f"materials_{format}"
    )
    
    # 返回文件响应
    media_type = 'text/csv' if format == 'csv' else 'text/plain'
    return Response(
        content=content,
        media_type=media_type,
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )


@router.get(
    "/{material_id}",
    response_model=None,
    summary="获取原料详情",
    description="根据ID获取原料详细信息"
)
async def get_material_detail(
    material_id: int = Path(..., gt=0, description="原料ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取原料详情"""
    material = await MaterialService.get_material_detail(db, material_id)
    return SuccessResponse(
        data=material.model_dump(mode='json'),
        msg="查询成功"
    )


@router.post(
    "/create",
    response_model=None,
    summary="创建新原料",
    description="创建新的原料信息"
)
async def create_material(
    material_data: MaterialCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建新原料"""
    material = await MaterialService.create_material(db, material_data)
    return SuccessResponse(
        data=material.model_dump(mode='json'),
        msg="原料创建成功"
    )


@router.put(
    "/{material_id}",
    response_model=None,
    summary="更新原料信息",
    description="更新现有原料的信息"
)
async def update_material(
    material_id: int = Path(..., gt=0, description="原料ID"),
    material_data: MaterialUpdateRequest = ...,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新原料信息"""
    material = await MaterialService.update_material(db, material_id, material_data)
    return SuccessResponse(
        data=material.model_dump(mode='json'),
        msg="原料更新成功"
    )


@router.delete(
    "/{material_id}",
    response_model=None,
    summary="删除原料",
    description="删除指定原料"
)
async def delete_material(
    material_id: int = Path(..., gt=0, description="原料ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除原料"""
    await MaterialService.delete_material(db, material_id)
    return SuccessResponse(
        data=None,
        msg="原料删除成功"
    )


@router.post(
    "/batch/delete",
    response_model=None,
    summary="批量删除原料",
    description="批量删除多个原料"
)
async def batch_delete_materials(
    delete_data: BatchDeleteRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """批量删除原料"""
    count = await MaterialService.batch_delete_materials(db, delete_data)
    return SuccessResponse(
        data={"deleted_count": count},
        msg=f"成功删除 {count} 个原料"
    )


@router.get(
    "/config/categories",
    response_model=None,
    summary="获取原料类别列表",
    description="获取所有可用的原料类别"
)
async def get_categories(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取原料类别列表"""
    categories = await MaterialService.get_categories(db)
    return SuccessResponse(
        data=[c.model_dump(mode='json') for c in categories],
        msg="查询成功"
    )


@router.get(
    "/config/suppliers",
    response_model=None,
    summary="获取供应商列表",
    description="获取系统中所有供应商（去重）"
)
async def get_suppliers(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取供应商列表"""
    suppliers = await MaterialService.get_suppliers(db)
    return SuccessResponse(
        data=suppliers,
        msg="查询成功"
    )

