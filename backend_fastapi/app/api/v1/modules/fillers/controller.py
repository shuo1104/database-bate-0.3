# -*- coding: utf-8 -*-
"""
填料管理Controller
"""

from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.common.response import SuccessResponse
from app.utils.export_helper import ExportHelper
from app.api.v1.modules.fillers.service import FillerService
from app.api.v1.modules.fillers.schema import (
    FillerCreateRequest,
    FillerUpdateRequest,
    FillerQueryParams,
    BatchDeleteRequest
)


router = APIRouter()


# ==================== 配置类路由（必须在动态路由之前） ====================

@router.get(
    "/config/types",
    response_model=None,
    summary="获取填料类型列表",
    description="获取所有可用的填料类型"
)
async def get_filler_types(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取填料类型列表"""
    types = await FillerService.get_filler_types(db)
    return SuccessResponse(
        data=[t.model_dump(mode='json') for t in types],
        msg="查询成功"
    )


@router.get(
    "/config/suppliers",
    response_model=None,
    summary="获取供应商列表",
    description="获取系统中所有填料供应商（去重）"
)
async def get_suppliers(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取供应商列表"""
    suppliers = await FillerService.get_suppliers(db)
    return SuccessResponse(
        data=suppliers,
        msg="查询成功"
    )


# ==================== CRUD 路由 ====================

@router.get(
    "/list",
    response_model=None,
    summary="获取填料列表",
    description="分页查询填料列表，支持多条件筛选"
)
async def get_filler_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    filler_type: str = Query(None, description="填料类型"),
    supplier: str = Query(None, description="供应商"),
    keyword: str = Query(None, description="关键词搜索"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取填料列表（分页）"""
    query_params = FillerQueryParams(
        filler_type=filler_type,
        supplier=supplier,
        keyword=keyword
    )
    
    fillers, total = await FillerService.get_filler_list(
        db=db,
        page=page,
        page_size=page_size,
        query_params=query_params
    )
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    return SuccessResponse(
        data={
            "list": [f.model_dump(mode='json') for f in fillers],
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
    summary="导出填料列表",
    description="导出填料列表数据为CSV或TXT格式"
)
async def export_fillers(
    format: str = Query('csv', description="导出格式: csv 或 txt"),
    filler_type: str = Query(None, description="填料类型"),
    supplier: str = Query(None, description="供应商"),
    keyword: str = Query(None, description="关键词"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """导出填料列表"""
    query_params = FillerQueryParams(
        filler_type=filler_type,
        supplier=supplier,
        keyword=keyword
    )
    
    # 获取所有符合条件的填料
    fillers, _ = await FillerService.get_filler_list(
        db=db,
        page=1,
        page_size=10000,
        query_params=query_params
    )
    
    # 定义列映射
    column_mapping = {
        'FillerID': '填料ID',
        'TradeName': '商品名称',
        'FillerTypeName': '填料类型',
        'Supplier': '供应商',
        'ParticleSize': '粒径',
        'IsSilanized': '是否硅烷化',
        'CouplingAgent': '偶联剂',
        'SurfaceArea': '比表面积',
    }
    
    # 准备导出数据
    export_data = ExportHelper.prepare_export_data(fillers, column_mapping)
    
    # 导出
    content, filename = ExportHelper.export(
        data=export_data,
        columns=list(column_mapping.values()),
        format=format,
        filename=f"fillers_{format}"
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
    "/{filler_id}",
    response_model=None,
    summary="获取填料详情",
    description="根据ID获取填料详细信息"
)
async def get_filler_detail(
    filler_id: int = Path(..., gt=0, description="填料ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取填料详情"""
    filler = await FillerService.get_filler_detail(db, filler_id)
    return SuccessResponse(
        data=filler.model_dump(mode='json'),
        msg="查询成功"
    )


@router.post(
    "/create",
    response_model=None,
    summary="创建新填料",
    description="创建新的填料记录"
)
async def create_filler(
    filler_data: FillerCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建新填料"""
    filler = await FillerService.create_filler(db, filler_data)
    return SuccessResponse(
        data=filler.model_dump(mode='json'),
        msg="填料创建成功"
    )


@router.post(
    "/batch/delete",
    response_model=None,
    summary="批量删除填料",
    description="批量删除多个填料"
)
async def batch_delete_fillers(
    delete_data: BatchDeleteRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """批量删除填料"""
    count = await FillerService.batch_delete_fillers(db, delete_data)
    return SuccessResponse(
        data={"deleted_count": count},
        msg=f"成功删除 {count} 个填料"
    )


@router.get(
    "/{filler_id}",
    response_model=None,
    summary="获取填料详情",
    description="根据ID获取填料详细信息"
)
async def get_filler_detail(
    filler_id: int = Path(..., gt=0, description="填料ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取填料详情"""
    filler = await FillerService.get_filler_detail(db, filler_id)
    return SuccessResponse(
        data=filler.model_dump(mode='json'),
        msg="查询成功"
    )


@router.put(
    "/{filler_id}",
    response_model=None,
    summary="更新填料信息",
    description="更新现有填料的信息"
)
async def update_filler(
    filler_id: int = Path(..., gt=0, description="填料ID"),
    filler_data: FillerUpdateRequest = ...,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新填料信息"""
    filler = await FillerService.update_filler(db, filler_id, filler_data)
    return SuccessResponse(
        data=filler.model_dump(mode='json'),
        msg="填料更新成功"
    )


@router.delete(
    "/{filler_id}",
    response_model=None,
    summary="删除填料",
    description="删除指定填料"
)
async def delete_filler(
    filler_id: int = Path(..., gt=0, description="填料ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除填料"""
    await FillerService.delete_filler(db, filler_id)
    return SuccessResponse(
        data=None,
        msg="填料删除成功"
    )


@router.get(
    "/export",
    response_model=None,
    summary="导出填料列表",
    description="导出填料列表数据为CSV或TXT格式"
)
async def export_fillers(
    format: str = Query('csv', description="导出格式: csv 或 txt"),
    filler_type: str = Query(None, description="填料类型"),
    supplier: str = Query(None, description="供应商"),
    keyword: str = Query(None, description="关键词"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """导出填料列表"""
    query_params = FillerQueryParams(
        filler_type=filler_type,
        supplier=supplier,
        keyword=keyword
    )
    
    # 获取所有符合条件的填料
    fillers, _ = await FillerService.get_filler_list(
        db=db,
        page=1,
        page_size=10000,
        query_params=query_params
    )
    
    # 定义列映射
    column_mapping = {
        'FillerID': '填料ID',
        'TradeName': '商品名称',
        'FillerTypeName': '填料类型',
        'Supplier': '供应商',
        'ParticleSize': '粒径',
        'IsSilanized': '是否硅烷化',
        'CouplingAgent': '偶联剂',
        'SurfaceArea': '比表面积',
    }
    
    # 准备导出数据
    export_data = ExportHelper.prepare_export_data(fillers, column_mapping)
    
    # 导出
    content, filename = ExportHelper.export(
        data=export_data,
        columns=list(column_mapping.values()),
        format=format,
        filename=f"fillers_{format}"
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

