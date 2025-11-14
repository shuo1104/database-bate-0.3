# -*- coding: utf-8 -*-
"""
项目管理CRUD操作
数据访问层 - 负责数据库操作
"""

from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.modules.projects.model import (
    ProjectModel,
    ProjectTypeModel,
    FormulaCompositionModel,
    TestResultInkModel,
    TestResultCoatingModel,
    TestResult3DPrintModel,
    TestResultCompositeModel
)
from app.core.logger import logger


class ProjectCRUD:
    """项目CRUD操作类"""
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        project_id: int
    ) -> Optional[ProjectModel]:
        """
        根据ID查询项目
        
        Args:
            db: 数据库会话
            project_id: 项目ID
        
        Returns:
            项目对象或None
        """
        try:
            stmt = (
                select(ProjectModel)
                .options(selectinload(ProjectModel.project_type))
                .options(
                    selectinload(ProjectModel.compositions).selectinload(FormulaCompositionModel.material)
                )
                .options(
                    selectinload(ProjectModel.compositions).selectinload(FormulaCompositionModel.filler)
                )
                .where(ProjectModel.ProjectID == project_id)
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"queryprojectfailed: {e}")
            raise
    
    @staticmethod
    async def get_list_paginated(
        db: AsyncSession,
        page: int,
        page_size: int,
        project_type: Optional[str] = None,
        formulator: Optional[str] = None,
        date_start: Optional[date] = None,
        date_end: Optional[date] = None,
        keyword: Optional[str] = None,
        has_compositions: Optional[bool] = None,
        has_test_results: Optional[bool] = None
    ) -> Tuple[List[ProjectModel], int]:
        """
        分页查询项目列表
        
        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            project_type: 项目类型筛选
            formulator: 配方设计师筛选
            date_start: 开始日期
            date_end: 结束日期
            keyword: 关键词搜索
            has_compositions: 是否有配方成分
            has_test_results: 是否有测试结果
        
        Returns:
            (项目列表, 总数)
        """
        try:
            # 记录查询参数
            logger.info(f"projectquery参数: keyword={keyword}, has_compositions={has_compositions}, has_test_results={has_test_results}")
            
            # 构建查询条件
            conditions = []
            
            if project_type:
                # 关联项目类型表
                conditions.append(ProjectTypeModel.TypeName == project_type)
            
            if formulator:
                conditions.append(ProjectModel.FormulatorName == formulator)
            
            if date_start:
                conditions.append(ProjectModel.FormulationDate >= date_start)
            
            if date_end:
                conditions.append(ProjectModel.FormulationDate <= date_end)
            
            if keyword:
                conditions.append(
                    or_(
                        ProjectModel.ProjectName.like(f"%{keyword}%"),
                        ProjectModel.FormulaCode.like(f"%{keyword}%")
                    )
                )
            
            # 筛选有配方成分的项目
            if has_compositions is not None:
                if has_compositions:
                    # 只显示有配方成分的项目
                    # 先查询有配方成分的项目ID列表用于调试
                    comp_ids_result = await db.execute(select(FormulaCompositionModel.ProjectID_FK).distinct())
                    comp_ids = [row[0] for row in comp_ids_result.all()]
                    logger.info(f"有formula成分的projectID列表: {comp_ids}")
                    
                    conditions.append(
                        ProjectModel.ProjectID.in_(
                            select(FormulaCompositionModel.ProjectID_FK).distinct()
                        )
                    )
                else:
                    # 只显示没有配方成分的项目
                    conditions.append(
                        ProjectModel.ProjectID.notin_(
                            select(FormulaCompositionModel.ProjectID_FK).distinct()
                        )
                    )
            
            # 筛选有测试结果的项目
            if has_test_results is not None:
                if has_test_results:
                    # 只显示有测试结果的项目（任一类型）
                    # 先查询有测试结果的项目ID列表用于调试
                    ink_ids_result = await db.execute(select(TestResultInkModel.ProjectID_FK).distinct())
                    ink_ids = [row[0] for row in ink_ids_result.all()]
                    coating_ids_result = await db.execute(select(TestResultCoatingModel.ProjectID_FK).distinct())
                    coating_ids = [row[0] for row in coating_ids_result.all()]
                    print3d_ids_result = await db.execute(select(TestResult3DPrintModel.ProjectID_FK).distinct())
                    print3d_ids = [row[0] for row in print3d_ids_result.all()]
                    composite_ids_result = await db.execute(select(TestResultCompositeModel.ProjectID_FK).distinct())
                    composite_ids = [row[0] for row in composite_ids_result.all()]
                    all_test_ids = set(ink_ids + coating_ids + print3d_ids + composite_ids)
                    logger.info(f"有testresult的projectID列表: {all_test_ids}")
                    
                    conditions.append(
                        or_(
                            ProjectModel.ProjectID.in_(
                                select(TestResultInkModel.ProjectID_FK).distinct()
                            ),
                            ProjectModel.ProjectID.in_(
                                select(TestResultCoatingModel.ProjectID_FK).distinct()
                            ),
                            ProjectModel.ProjectID.in_(
                                select(TestResult3DPrintModel.ProjectID_FK).distinct()
                            ),
                            ProjectModel.ProjectID.in_(
                                select(TestResultCompositeModel.ProjectID_FK).distinct()
                            )
                        )
                    )
                else:
                    # 只显示没有测试结果的项目
                    conditions.append(
                        and_(
                            ProjectModel.ProjectID.notin_(
                                select(TestResultInkModel.ProjectID_FK).distinct()
                            ),
                            ProjectModel.ProjectID.notin_(
                                select(TestResultCoatingModel.ProjectID_FK).distinct()
                            ),
                            ProjectModel.ProjectID.notin_(
                                select(TestResult3DPrintModel.ProjectID_FK).distinct()
                            ),
                            ProjectModel.ProjectID.notin_(
                                select(TestResultCompositeModel.ProjectID_FK).distinct()
                            )
                        )
                    )
            
            # 查询总数
            count_stmt = (
                select(func.count(ProjectModel.ProjectID))
                .select_from(ProjectModel)
                .join(
                    ProjectTypeModel,
                    ProjectModel.ProjectType_FK == ProjectTypeModel.TypeID,
                    isouter=True
                )
            )
            if conditions:
                count_stmt = count_stmt.where(and_(*conditions))
            
            total_result = await db.execute(count_stmt)
            total = total_result.scalar() or 0
            
            # 查询数据
            offset = (page - 1) * page_size
            stmt = (
                select(ProjectModel)
                .options(selectinload(ProjectModel.project_type))
                .join(
                    ProjectTypeModel,
                    ProjectModel.ProjectType_FK == ProjectTypeModel.TypeID,
                    isouter=True
                )
                .order_by(ProjectModel.ProjectID.desc())
                .offset(offset)
                .limit(page_size)
            )
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            result = await db.execute(stmt)
            projects = result.scalars().all()
            
            logger.info(f"queryresult: total={total}, returned={len(projects)}, projectIDs={[p.ProjectID for p in projects]}")
            
            return list(projects), total
            
        except Exception as e:
            logger.error(f"分页queryprojectfailed: {e}")
            raise
    
    @staticmethod
    async def create_project(
        db: AsyncSession,
        project_name: str,
        project_type_fk: int,
        formulator_name: str,
        formulation_date: date,
        substrate_application: Optional[str] = None
    ) -> ProjectModel:
        """
        创建新项目
        
        Args:
            db: 数据库会话
            project_name: 项目名称
            project_type_fk: 项目类型ID
            formulator_name: 配方设计师
            formulation_date: 配方设计日期
            substrate_application: 目标基材
        
        Returns:
            创建的项目对象
        """
        try:
            # 生成配方编码
            formula_code = await ProjectCRUD._generate_formula_code(
                db, project_type_fk, formulator_name, formulation_date
            )
            
            project = ProjectModel(
                ProjectName=project_name,
                ProjectType_FK=project_type_fk,
                SubstrateApplication=substrate_application,
                FormulatorName=formulator_name,
                FormulationDate=formulation_date,
                FormulaCode=formula_code
            )
            
            db.add(project)
            await db.flush()
            await db.refresh(project)
            
            return project
            
        except Exception as e:
            logger.error(f"createprojectfailed: {e}")
            raise
    
    @staticmethod
    async def update_project(
        db: AsyncSession,
        project_id: int,
        **kwargs
    ) -> bool:
        """
        更新项目信息
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            **kwargs: 要更新的字段
        
        Returns:
            是否成功
        """
        try:
            # 过滤None值
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return True
            
            stmt = (
                update(ProjectModel)
                .where(ProjectModel.ProjectID == project_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            
            return True
            
        except Exception as e:
            logger.error(f"updateprojectfailed: {e}")
            return False
    
    @staticmethod
    async def delete_project(
        db: AsyncSession,
        project_id: int
    ) -> bool:
        """
        删除项目
        
        Args:
            db: 数据库会话
            project_id: 项目ID
        
        Returns:
            是否成功
        """
        try:
            stmt = delete(ProjectModel).where(ProjectModel.ProjectID == project_id)
            await db.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"deletedprojectfailed: {e}")
            return False
    
    @staticmethod
    async def batch_delete_projects(
        db: AsyncSession,
        project_ids: List[int]
    ) -> int:
        """
        批量删除项目
        
        Args:
            db: 数据库会话
            project_ids: 项目ID列表
        
        Returns:
            删除的数量
        """
        try:
            stmt = delete(ProjectModel).where(ProjectModel.ProjectID.in_(project_ids))
            result = await db.execute(stmt)
            return result.rowcount
        except Exception as e:
            logger.error(f"batchdeletedprojectfailed: {e}")
            raise
    
    @staticmethod
    async def _generate_formula_code(
        db: AsyncSession,
        project_type_fk: int,
        formulator_name: str,
        formulation_date: date
    ) -> str:
        """
        生成配方编码
        格式: 设计师缩写-日期-类型代码-序号
        例如: ZS-01012024-INK-01
        
        Args:
            db: 数据库会话
            project_type_fk: 项目类型ID
            formulator_name: 配方设计师
            formulation_date: 配方设计日期
        
        Returns:
            配方编码
        """
        try:
            # 获取类型代码
            type_stmt = select(ProjectTypeModel.TypeCode).where(
                ProjectTypeModel.TypeID == project_type_fk
            )
            type_result = await db.execute(type_stmt)
            type_code = type_result.scalar() or "XXX"
            
            # 计算当天相同类型的序号
            count_stmt = select(func.count(ProjectModel.ProjectID)).where(
                and_(
                    ProjectModel.FormulationDate == formulation_date,
                    ProjectModel.ProjectType_FK == project_type_fk
                )
            )
            count_result = await db.execute(count_stmt)
            sequence_num = (count_result.scalar() or 0) + 1
            sequence_str = f"{sequence_num:02d}"
            
            # 生成设计师缩写
            initials = "".join(c for c in formulator_name if c.isupper()) or formulator_name[:2].upper()
            
            # 生成日期字符串
            date_str = formulation_date.strftime('%d%m%Y')
            
            # 组合配方编码
            formula_code = f"{initials}-{date_str}-{type_code}-{sequence_str}"
            
            return formula_code
            
        except Exception as e:
            logger.error(f"生成formula编码failed: {e}")
            raise


class ProjectTypeCRUD:
    """项目类型CRUD操作类"""
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[ProjectTypeModel]:
        """获取所有项目类型"""
        try:
            stmt = select(ProjectTypeModel).order_by(ProjectTypeModel.TypeName)
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"queryproject类型failed: {e}")
            raise
    
    @staticmethod
    async def get_formulators(db: AsyncSession) -> List[str]:
        """获取所有配方设计师列表（去重）"""
        try:
            stmt = (
                select(ProjectModel.FormulatorName)
                .where(ProjectModel.FormulatorName.isnot(None))
                .where(ProjectModel.FormulatorName != "")
                .distinct()
                .order_by(ProjectModel.FormulatorName)
            )
            result = await db.execute(stmt)
            return [row[0] for row in result.all()]
        except Exception as e:
            logger.error(f"queryformula设计师列表failed: {e}")
            raise


class CompositionCRUD:
    """配方成分CRUD操作类"""
    
    @staticmethod
    async def get_by_project_id(
        db: AsyncSession,
        project_id: int
    ) -> List[FormulaCompositionModel]:
        """获取项目的所有配方成分"""
        try:
            from sqlalchemy.orm import joinedload
            stmt = (
                select(FormulaCompositionModel)
                .options(
                    joinedload(FormulaCompositionModel.material),
                    joinedload(FormulaCompositionModel.filler)
                )
                .where(FormulaCompositionModel.ProjectID_FK == project_id)
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"queryformula成分failed: {e}")
            raise
    
    @staticmethod
    async def create_composition(
        db: AsyncSession,
        project_id: int,
        material_id: Optional[int],
        filler_id: Optional[int],
        weight_percentage: float,
        addition_method: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> FormulaCompositionModel:
        """创建配方成分"""
        try:
            composition = FormulaCompositionModel(
                ProjectID_FK=project_id,
                MaterialID_FK=material_id,
                FillerID_FK=filler_id,
                WeightPercentage=weight_percentage,
                AdditionMethod=addition_method,
                Remarks=remarks
            )
            db.add(composition)
            await db.flush()
            await db.refresh(composition)
            return composition
        except Exception as e:
            logger.error(f"createformula成分failed: {e}")
            raise
    
    @staticmethod
    async def update_composition(
        db: AsyncSession,
        composition_id: int,
        material_id: Optional[int] = None,
        filler_id: Optional[int] = None,
        weight_percentage: Optional[float] = None,
        addition_method: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> Optional[FormulaCompositionModel]:
        """更新配方成分"""
        try:
            # 先查询是否存在
            stmt = select(FormulaCompositionModel).where(
                FormulaCompositionModel.CompositionID == composition_id
            )
            result = await db.execute(stmt)
            composition = result.scalar_one_or_none()
            
            if not composition:
                return None
            
            # 更新字段
            if material_id is not None:
                composition.MaterialID_FK = material_id
            if filler_id is not None:
                composition.FillerID_FK = filler_id
            if weight_percentage is not None:
                composition.WeightPercentage = weight_percentage
            if addition_method is not None:
                composition.AdditionMethod = addition_method
            if remarks is not None:
                composition.Remarks = remarks
            
            await db.flush()
            await db.refresh(composition)
            return composition
        except Exception as e:
            logger.error(f"updateformula成分failed: {e}")
            raise
    
    @staticmethod
    async def delete_composition(
        db: AsyncSession,
        composition_id: int
    ) -> bool:
        """删除配方成分"""
        try:
            stmt = delete(FormulaCompositionModel).where(
                FormulaCompositionModel.CompositionID == composition_id
            )
            await db.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"deletedformula成分failed: {e}")
            return False

