# -*- coding: utf-8 -*-
"""
项目导出服务（性能优化版本）
解决 N+1 查询问题，使用流式导出
"""

import csv
import io
from typing import AsyncGenerator, List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.modules.projects.model import (
    ProjectModel,
    FormulaCompositionModel
)
from app.api.v1.modules.projects.schema import ProjectQueryParams
from app.api.v1.modules.test_results.model import (
    TestResultInkModel,
    TestResultCoatingModel,
    TestResult3DPrintModel,
    TestResultCompositeModel
)
from app.core.logger import logger


class ProjectExportService:
    """项目导出服务（性能优化版）"""
    
    # 导出限制常量
    MAX_EXPORT_COUNT = 50000  # 最大导出数量
    BATCH_SIZE = 100  # 每批处理的项目数
    
    @staticmethod
    async def get_projects_with_relations_batch(
        db: AsyncSession,
        query_params: ProjectQueryParams,
        offset: int,
        limit: int
    ) -> List[ProjectModel]:
        """
        批量获取项目及其关联数据（使用 selectinload 避免 N+1 问题）
        
        Args:
            db: 数据库会话
            query_params: 查询参数
            offset: 偏移量
            limit: 限制数量
        
        Returns:
            项目列表（包含关联的配方成分数据）
        """
        # 构建基础查询
        stmt = select(ProjectModel).options(
            # 使用 selectinload 一次性加载所有关联数据
            selectinload(ProjectModel.compositions)
                .selectinload(FormulaCompositionModel.material),
            selectinload(ProjectModel.compositions)
                .selectinload(FormulaCompositionModel.filler),
            selectinload(ProjectModel.project_type)
        )
        
        # 应用筛选条件
        if query_params.project_type:
            stmt = stmt.join(ProjectModel.project_type).where(
                ProjectModel.project_type.has(TypeName=query_params.project_type)
            )
        
        if query_params.formulator:
            stmt = stmt.where(ProjectModel.FormulatorName == query_params.formulator)
        
        if query_params.keyword:
            from sqlalchemy import or_
            keyword_filter = f"%{query_params.keyword}%"
            stmt = stmt.where(
                or_(
                    ProjectModel.ProjectName.ilike(keyword_filter),
                    ProjectModel.FormulaCode.ilike(keyword_filter),
                    ProjectModel.SubstrateApplication.ilike(keyword_filter)
                )
            )
        
        # 排序并分页
        stmt = stmt.order_by(ProjectModel.CreatedAt.desc())
        stmt = stmt.offset(offset).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_test_results_batch(
        db: AsyncSession,
        project_ids: List[int]
    ) -> Dict[int, Any]:
        """
        批量获取测试结果（避免 N+1 问题）
        
        Args:
            db: 数据库会话
            project_ids: 项目ID列表
        
        Returns:
            {project_id: test_result} 映射字典
        """
        if not project_ids:
            return {}
        
        results_map = {}
        
        # 批量查询各类型测试结果
        for model_class in [
            TestResultInkModel,
            TestResultCoatingModel,
            TestResult3DPrintModel,
            TestResultCompositeModel
        ]:
            stmt = select(model_class).where(
                model_class.ProjectID_FK.in_(project_ids)
            )
            result = await db.execute(stmt)
            test_results = result.scalars().all()
            
            for tr in test_results:
                project_id = tr.ProjectID_FK
                if project_id not in results_map:
                    results_map[project_id] = tr
        
        return results_map
    
    @staticmethod
    async def stream_export_csv(
        db: AsyncSession,
        query_params: ProjectQueryParams
    ) -> AsyncGenerator[str, None]:
        """
        流式导出CSV（按批次处理，节省内存）
        
        Args:
            db: 数据库会话
            query_params: 查询参数
        
        Yields:
            CSV行数据（字符串）
        """
        # 添加 UTF-8 BOM
        yield '\ufeff'
        
        # 生成表头
        header_cols = [
            '项目ID', '项目名称', '项目类型', '配方编号', '配方设计师', '配方日期', '目标基材',
            '成分序号', '成分类型', '成分名称', '重量百分比(%)', '掺入方法', '成分备注',
            '总重量百分比(%)', '测试数据'
        ]
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(header_cols)
        yield output.getvalue()
        output.close()
        
        # 分批处理项目
        offset = 0
        total_exported = 0
        
        while total_exported < ProjectExportService.MAX_EXPORT_COUNT:
            # 批量获取项目及关联数据
            projects = await ProjectExportService.get_projects_with_relations_batch(
                db=db,
                query_params=query_params,
                offset=offset,
                limit=ProjectExportService.BATCH_SIZE
            )
            
            if not projects:
                break  # 没有更多数据
            
            # 批量获取测试结果
            project_ids = [p.ProjectID for p in projects]
            test_results_map = await ProjectExportService.get_test_results_batch(db, project_ids)
            
            # 处理当前批次
            output = io.StringIO()
            writer = csv.writer(output)
            
            for project in projects:
                # 获取测试结果字符串
                test_result_str = ''
                if project.ProjectID in test_results_map:
                    test_result = test_results_map[project.ProjectID]
                    test_dict = {}
                    for key in dir(test_result):
                        if not key.startswith('_') and key not in ['ResultID', 'ProjectID_FK', 'metadata', 'registry']:
                            value = getattr(test_result, key, None)
                            if value and not callable(value):
                                test_dict[key] = value
                    
                    test_items = [f'{k}={v}' for k, v in test_dict.items() if v]
                    test_result_str = '; '.join(test_items)
                
                # 获取配方成分
                compositions = project.compositions or []
                total_weight = sum(float(c.WeightPercentage) for c in compositions) if compositions else 0
                
                if compositions:
                    # 每个成分一行
                    for idx, comp in enumerate(compositions):
                        comp_type = '原料' if comp.MaterialID_FK else '填料'
                        comp_name = ''
                        if comp.material:
                            comp_name = comp.material.TradeName
                        elif comp.filler:
                            comp_name = comp.filler.TradeName
                        
                        row = [
                            project.ProjectID,
                            project.ProjectName,
                            project.project_type.TypeName if project.project_type else '',
                            project.FormulaCode or '',
                            project.FormulatorName or '',
                            str(project.FormulationDate) if project.FormulationDate else '',
                            project.SubstrateApplication or '',
                            idx + 1,
                            comp_type,
                            comp_name,
                            float(comp.WeightPercentage),
                            comp.AdditionMethod or '',
                            comp.Remarks or '',
                            f'{total_weight:.2f}' if idx == 0 else '',
                            test_result_str if idx == 0 else ''
                        ]
                        writer.writerow(row)
                else:
                    # 没有成分，输出项目基本信息
                    row = [
                        project.ProjectID,
                        project.ProjectName,
                        project.project_type.TypeName if project.project_type else '',
                        project.FormulaCode or '',
                        project.FormulatorName or '',
                        str(project.FormulationDate) if project.FormulationDate else '',
                        project.SubstrateApplication or '',
                        '', '', '', '', '', '',
                        '0.00',
                        test_result_str
                    ]
                    writer.writerow(row)
            
            # 输出当前批次
            yield output.getvalue()
            output.close()
            
            # 更新计数器
            total_exported += len(projects)
            offset += ProjectExportService.BATCH_SIZE
            
            logger.info(f"Export progress: {total_exported} 个project")
            
            # 如果本批次数据不足，说明已经到达末尾
            if len(projects) < ProjectExportService.BATCH_SIZE:
                break
    
    @staticmethod
    async def stream_export_txt(
        db: AsyncSession,
        query_params: ProjectQueryParams
    ) -> AsyncGenerator[str, None]:
        """
        流式导出TXT（按批次处理，节省内存）
        
        Args:
            db: 数据库会话
            query_params: 查询参数
        
        Yields:
            TXT行数据（字符串）
        """
        # 添加 UTF-8 BOM
        yield '\ufeff'
        
        # 生成表头
        header_cols = [
            '项目ID', '项目名称', '项目类型', '配方编号', '配方设计师', '配方日期', '目标基材',
            '成分序号', '成分类型', '成分名称', '重量百分比(%)', '掺入方法', '成分备注',
            '总重量百分比(%)', '测试数据'
        ]
        yield '\t'.join(header_cols) + '\n'
        
        # 分批处理项目
        offset = 0
        total_exported = 0
        
        while total_exported < ProjectExportService.MAX_EXPORT_COUNT:
            # 批量获取项目及关联数据
            projects = await ProjectExportService.get_projects_with_relations_batch(
                db=db,
                query_params=query_params,
                offset=offset,
                limit=ProjectExportService.BATCH_SIZE
            )
            
            if not projects:
                break
            
            # 批量获取测试结果
            project_ids = [p.ProjectID for p in projects]
            test_results_map = await ProjectExportService.get_test_results_batch(db, project_ids)
            
            # 构建当前批次的TXT内容
            batch_lines = []
            
            for project in projects:
                # 获取测试结果字符串
                test_result_str = ''
                if project.ProjectID in test_results_map:
                    test_result = test_results_map[project.ProjectID]
                    test_dict = {}
                    for key in dir(test_result):
                        if not key.startswith('_') and key not in ['ResultID', 'ProjectID_FK', 'metadata', 'registry']:
                            value = getattr(test_result, key, None)
                            if value and not callable(value):
                                test_dict[key] = value
                    
                    test_items = [f'{k}={v}' for k, v in test_dict.items() if v]
                    test_result_str = '; '.join(test_items)
                
                # 获取配方成分
                compositions = project.compositions or []
                total_weight = sum(float(c.WeightPercentage) for c in compositions) if compositions else 0
                
                if compositions:
                    for idx, comp in enumerate(compositions):
                        comp_type = '原料' if comp.MaterialID_FK else '填料'
                        comp_name = ''
                        if comp.material:
                            comp_name = comp.material.TradeName
                        elif comp.filler:
                            comp_name = comp.filler.TradeName
                        
                        row_data = [
                            str(project.ProjectID),
                            project.ProjectName,
                            project.project_type.TypeName if project.project_type else '',
                            project.FormulaCode or '',
                            project.FormulatorName or '',
                            str(project.FormulationDate) if project.FormulationDate else '',
                            project.SubstrateApplication or '',
                            str(idx + 1),
                            comp_type,
                            comp_name,
                            str(float(comp.WeightPercentage)),
                            comp.AdditionMethod or '',
                            comp.Remarks or '',
                            f'{total_weight:.2f}' if idx == 0 else '',
                            test_result_str if idx == 0 else ''
                        ]
                        batch_lines.append('\t'.join(row_data) + '\n')
                else:
                    row_data = [
                        str(project.ProjectID),
                        project.ProjectName,
                        project.project_type.TypeName if project.project_type else '',
                        project.FormulaCode or '',
                        project.FormulatorName or '',
                        str(project.FormulationDate) if project.FormulationDate else '',
                        project.SubstrateApplication or '',
                        '', '', '', '', '', '',
                        '0.00',
                        test_result_str
                    ]
                    batch_lines.append('\t'.join(row_data) + '\n')
            
            # 输出当前批次
            yield ''.join(batch_lines)
            
            # 更新计数器
            total_exported += len(projects)
            offset += ProjectExportService.BATCH_SIZE
            
            logger.info(f"Export progress: {total_exported} 个project")
            
            if len(projects) < ProjectExportService.BATCH_SIZE:
                break

