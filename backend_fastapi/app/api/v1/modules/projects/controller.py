# -*- coding: utf-8 -*-
"""
项目管理Controller
API路由层 - 处理HTTP请求
"""

from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.common.response import SuccessResponse, PaginatedResponse
from app.utils.export_helper import ExportHelper
from app.utils.chart_generator import ChartGenerator
from app.core.base_schema import PaginationParams
from app.api.v1.modules.projects.service import ProjectService, CompositionService
from app.api.v1.modules.projects.schema import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectQueryParams,
    ProjectBasicResponse,
    ProjectDetailResponse,
    ProjectTypeResponse,
    CompositionCreateRequest,
    CompositionUpdateRequest,
    CompositionResponse,
    BatchDeleteRequest
)


# 创建路由
router = APIRouter()


# ==================== 项目管理接口 ====================
@router.get(
    "/list",
    response_model=None,
    summary="获取项目列表",
    description="分页查询项目列表，支持多条件筛选"
)
async def get_project_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    project_type: str = Query(None, description="项目类型"),
    formulator: str = Query(None, description="配方设计师"),
    date_start: str = Query(None, description="开始日期(YYYY-MM-DD)"),
    date_end: str = Query(None, description="结束日期(YYYY-MM-DD)"),
    keyword: str = Query(None, description="关键词搜索"),
    has_compositions: bool = Query(None, description="是否有配方成分"),
    has_test_results: bool = Query(None, description="是否有测试结果"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目列表（分页）
    
    需要认证: 是
    
    查询参数:
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    - **project_type**: 项目类型筛选
    - **formulator**: 配方设计师筛选
    - **date_start**: 开始日期
    - **date_end**: 结束日期
    - **keyword**: 关键词（搜索项目名称或配方编码）
    - **has_compositions**: 是否有配方成分
    - **has_test_results**: 是否有测试结果
    """
    # 构建查询参数
    query_params = ProjectQueryParams(
        project_type=project_type,
        formulator=formulator,
        date_start=date_start,
        date_end=date_end,
        keyword=keyword,
        has_compositions=has_compositions,
        has_test_results=has_test_results
    )
    
    # 查询数据
    projects, total = await ProjectService.get_project_list(
        db=db,
        page=page,
        page_size=page_size,
        query_params=query_params
    )
    
    # 构建分页响应
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    return SuccessResponse(
        data={
            "list": [p.model_dump(mode='json') for p in projects],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        },
        msg="查询成功"
    )


# ==================== 数据导出接口 ====================
@router.get(
    "/export",
    response_model=None,
    summary="导出项目完整信息（性能优化版）",
    description="流式导出项目列表数据为CSV或TXT格式，包含项目基本信息、配方成分和测试结果。使用批量查询和流式响应，支持大数据集导出"
)
async def export_projects(
    format: str = Query('csv', description="导出格式: csv 或 txt"),
    project_type: str = Query(None, description="项目类型"),
    formulator: str = Query(None, description="配方设计师"),
    keyword: str = Query(None, description="关键词搜索"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    导出项目完整信息（性能优化版）
    
    **性能优化**:
    - ✅ 使用 selectinload 解决 N+1 查询问题
    - ✅ 批量处理（每批100条），避免内存溢出
    - ✅ 流式响应，边生成边输出
    - ✅ 最大导出限制：50000条记录
    
    需要认证: 是
    
    查询参数:
    - **format**: 导出格式 (csv 或 txt)
    - **project_type**: 项目类型筛选
    - **formulator**: 配方设计师筛选
    - **keyword**: 关键词搜索
    """
    from app.api.v1.modules.projects.export_service import ProjectExportService
    from fastapi.responses import StreamingResponse
    from datetime import datetime
    
    # 构建查询参数
    query_params = ProjectQueryParams(
        project_type=project_type,
        formulator=formulator,
        keyword=keyword
    )
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"projects_export_{timestamp}.{format}"
    
    # 选择导出格式
    if format == 'txt':
        stream_generator = ProjectExportService.stream_export_txt(db, query_params)
        media_type = 'text/plain; charset=utf-8'
    else:
        stream_generator = ProjectExportService.stream_export_csv(db, query_params)
        media_type = 'text/csv; charset=utf-8'
    
    # 返回流式响应
    return StreamingResponse(
        stream_generator,
        media_type=media_type,
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Cache-Control': 'no-cache'
        }
    )


@router.get(
    "/export-image/{project_id}",
    response_model=None,
    summary="导出项目图片报告",
    description="导出包含项目信息表、配方成分柱状图、测试结果雷达图的PNG图片"
)
async def export_project_image(
    project_id: int = Path(..., gt=0, description="项目ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    导出项目完整报告图片
    
    需要认证: 是
    
    路径参数:
    - **project_id**: 项目ID
    
    返回:
    - PNG图片文件（包含项目信息表、配方成分柱状图、测试结果雷达图）
    """
    from app.api.v1.modules.test_results.service import TestResultService
    from app.api.v1.modules.projects.crud import ProjectCRUD
    from datetime import datetime
    
    # 获取项目详情
    project = await ProjectCRUD.get_by_id(db, project_id)
    if not project:
        return Response(
            content=b'Project not found',
            status_code=404,
            media_type='text/plain'
        )
    
    # 准备项目数据
    project_data = {
        'ProjectID': project.ProjectID,
        'ProjectName': project.ProjectName,
        'TypeName': project.project_type.TypeName if project.project_type else 'N/A',
        'FormulaCode': project.FormulaCode,
        'FormulatorName': project.FormulatorName,
        'FormulationDate': project.FormulationDate,
        'SubstrateApplication': project.SubstrateApplication,
    }
    
    # 获取配方成分
    compositions = []
    if project.compositions:
        for comp in project.compositions:
            comp_data = {
                'WeightPercentage': float(comp.WeightPercentage),
                'MaterialName': comp.material.TradeName if comp.material else None,
                'FillerName': comp.filler.TradeName if comp.filler else None,
                'Remarks': comp.Remarks if comp.Remarks else '',
            }
            compositions.append(comp_data)
    
    # 获取测试结果
    test_results = {}
    project_type_name = project_data['TypeName']
    if project_type_name and project_type_name != 'N/A':
        try:
            test_result = await TestResultService.get_test_result(db, project_id)
            if test_result:
                # 将测试结果转换为字典，并清理特殊字符
                char_replacements = {
                    '²': '^2',
                    '³': '^3',
                    '°': 'deg',
                    '℃': 'C',
                    'μ': 'u',
                    '·': '.',
                    '～': '~',
                    '—': '-'
                }
                test_results = {}
                for k, v in test_result.__dict__.items():
                    if not k.startswith('_') and k not in ['ResultID', 'ProjectID_FK', 'TestDate', 'Notes']:
                        # 如果值是字符串，替换特殊字符
                        if isinstance(v, str):
                            clean_v = v
                            for old_char, new_char in char_replacements.items():
                                clean_v = clean_v.replace(old_char, new_char)
                            test_results[k] = clean_v
                        else:
                            test_results[k] = v
        except Exception as e:
            # 如果获取测试结果失败，继续生成图片，只是不包含测试结果
            pass
    
    # 生成图片
    try:
        # 1. 创建项目信息表
        info_img = ChartGenerator.create_project_info_table(project_data)
        
        # 2. 创建配料信息表
        composition_table_img = ChartGenerator.create_composition_table(compositions)
        
        # 3. 创建配方成分柱状图
        bar_chart_bytes = ChartGenerator.create_composition_bar_chart(compositions)
        
        # 4. 创建测试结果表
        test_result_table_img = ChartGenerator.create_test_result_table(
            test_results, project_type_name
        )
        
        # 5. 创建测试结果雷达图
        radar_chart_bytes = ChartGenerator.create_test_result_radar_chart(
            test_results, project_type_name
        )
        
        # 6. 组合图片
        combined_image_bytes = ChartGenerator.combine_images_vertical(
            info_img, composition_table_img, bar_chart_bytes, 
            test_result_table_img, radar_chart_bytes
        )
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"project_{project_id}_{timestamp}.png"
        
        # 返回图片
        return Response(
            content=combined_image_bytes,
            media_type='image/png',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        import traceback
        error_msg = f"生成图片失败: {str(e)}\n{traceback.format_exc()}"
        return Response(
            content=error_msg.encode('utf-8'),
            status_code=500,
            media_type='text/plain; charset=utf-8'
        )


@router.get(
    "/{project_id}",
    response_model=None,
    summary="获取项目详情",
    description="根据ID获取项目详细信息，包含配方成分"
)
async def get_project_detail(
    project_id: int = Path(..., gt=0, description="项目ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目详情
    
    需要认证: 是
    
    路径参数:
    - **project_id**: 项目ID
    """
    project = await ProjectService.get_project_detail(db, project_id)
    return SuccessResponse(
        data=project.model_dump(mode='json'),
        msg="查询成功"
    )


@router.post(
    "/create",
    response_model=None,
    summary="创建新项目",
    description="创建新的化学配方项目"
)
async def create_project(
    project_data: ProjectCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新项目
    
    需要认证: 是
    
    请求体:
    - **project_name**: 项目名称（必填）
    - **project_type_fk**: 项目类型ID（必填）
    - **formulator_name**: 配方设计师（必填）
    - **formulation_date**: 配方设计日期（必填）
    - **substrate_application**: 目标基材或应用领域（可选）
    """
    project = await ProjectService.create_project(db, project_data)
    return SuccessResponse(
        data=project.model_dump(mode='json'),
        msg="项目创建成功"
    )


@router.put(
    "/{project_id}",
    response_model=None,
    summary="更新项目信息",
    description="更新现有项目的基本信息"
)
async def update_project(
    project_id: int = Path(..., gt=0, description="项目ID"),
    project_data: ProjectUpdateRequest = ...,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    更新项目信息
    
    需要认证: 是
    
    路径参数:
    - **project_id**: 项目ID
    
    请求体:（所有字段可选）
    - **project_name**: 项目名称
    - **project_type_fk**: 项目类型ID
    - **formulator_name**: 配方设计师
    - **formulation_date**: 配方设计日期
    - **substrate_application**: 目标基材或应用领域
    """
    project = await ProjectService.update_project(db, project_id, project_data)
    return SuccessResponse(
        data=project.model_dump(mode='json'),
        msg="项目更新成功"
    )


@router.delete(
    "/{project_id}",
    response_model=None,
    summary="删除项目",
    description="删除指定项目（级联删除配方成分和测试结果）"
)
async def delete_project(
    project_id: int = Path(..., gt=0, description="项目ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    删除项目
    
    需要认证: 是
    
    路径参数:
    - **project_id**: 项目ID
    
    注意: 删除项目会级联删除其关联的配方成分和测试结果
    """
    await ProjectService.delete_project(db, project_id)
    return SuccessResponse(
        data=None,
        msg="项目删除成功"
    )


@router.post(
    "/batch/delete",
    response_model=None,
    summary="批量删除项目",
    description="批量删除多个项目"
)
async def batch_delete_projects(
    delete_data: BatchDeleteRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    批量删除项目
    
    需要认证: 是
    
    请求体:
    - **ids**: 要删除的项目ID列表
    """
    count = await ProjectService.batch_delete_projects(db, delete_data)
    return SuccessResponse(
        data={"deleted_count": count},
        msg=f"成功删除 {count} 个项目"
    )


# ==================== 辅助接口 ====================
@router.get(
    "/config/types",
    response_model=None,
    summary="获取项目类型列表",
    description="获取所有可用的项目类型"
)
async def get_project_types(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目类型列表
    
    需要认证: 是
    
    返回所有可用的项目类型（喷墨、涂层、3D打印、复合材料等）
    """
    types = await ProjectService.get_project_types(db)
    return SuccessResponse(
        data=[t.model_dump(mode='json') for t in types],
        msg="查询成功"
    )


@router.get(
    "/config/formulators",
    response_model=None,
    summary="获取配方设计师列表",
    description="获取系统中所有配方设计师（去重）"
)
async def get_formulators(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取配方设计师列表
    
    需要认证: 是
    
    返回系统中所有出现过的配方设计师名称（用于筛选）
    """
    formulators = await ProjectService.get_formulators(db)
    return SuccessResponse(
        data=formulators,
        msg="查询成功"
    )


# ==================== 配方成分接口 ====================
@router.get(
    "/{project_id}/compositions",
    response_model=None,
    summary="获取项目配方成分",
    description="获取指定项目的所有配方成分"
)
async def get_project_compositions(
    project_id: int = Path(..., gt=0, description="项目ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目配方成分
    
    需要认证: 是
    
    路径参数:
    - **project_id**: 项目ID
    """
    compositions = await CompositionService.get_compositions_by_project(db, project_id)
    return SuccessResponse(
        data=[c.model_dump(mode='json') for c in compositions],
        msg="查询成功"
    )


@router.post(
    "/compositions/create",
    response_model=None,
    summary="添加配方成分",
    description="为项目添加新的配方成分"
)
async def create_composition(
    composition_data: CompositionCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    添加配方成分
    
    需要认证: 是
    
    请求体:
    - **project_id**: 项目ID（必填）
    - **material_id**: 原料ID（与filler_id至少填一个）
    - **filler_id**: 填料ID（与material_id至少填一个）
    - **weight_percentage**: 重量百分比（0-100.5）
    - **addition_method**: 掺入方法（可选）
    - **remarks**: 备注（可选）
    """
    composition = await CompositionService.create_composition(db, composition_data)
    return SuccessResponse(
        data=composition.model_dump(mode='json'),
        msg="配方成分添加成功"
    )


@router.put(
    "/compositions/{composition_id}",
    response_model=None,
    summary="更新配方成分",
    description="更新指定的配方成分"
)
async def update_composition(
    composition_id: int = Path(..., gt=0, description="成分ID"),
    composition_data: CompositionUpdateRequest = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    更新配方成分
    
    需要认证: 是
    
    请求体:
    - **material_id**: 原料ID（可选）
    - **filler_id**: 填料ID（可选）
    - **weight_percentage**: 重量百分比（可选）
    - **addition_method**: 掺入方法（可选）
    - **remarks**: 备注（可选）
    """
    composition = await CompositionService.update_composition(
        db, composition_id, composition_data
    )
    return SuccessResponse(
        data=composition.model_dump(mode='json'),
        msg="配方成分更新成功"
    )


@router.delete(
    "/compositions/{composition_id}",
    response_model=None,
    summary="删除配方成分",
    description="删除指定的配方成分"
)
async def delete_composition(
    composition_id: int = Path(..., gt=0, description="成分ID"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    删除配方成分
    
    需要认证: 是
    
    路径参数:
    - **composition_id**: 成分ID
    """
    await CompositionService.delete_composition(db, composition_id)
    return SuccessResponse(
        data=None,
        msg="配方成分删除成功"
    )

