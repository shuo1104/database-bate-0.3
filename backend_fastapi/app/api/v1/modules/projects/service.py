# -*- coding: utf-8 -*-
"""
项目管理Service
业务逻辑层 - 处理业务逻辑
"""

from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DataError

from app.api.v1.modules.projects.crud import (
    ProjectCRUD,
    ProjectTypeCRUD,
    CompositionCRUD
)
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
from app.core.logger import logger
from app.core.custom_exceptions import (
    RecordNotFoundException,
    DuplicateRecordException,
    DatabaseException,
    ValidationException,
    IntegrityConstraintException,
    BusinessLogicException,
)


class ProjectService:
    """项目服务类"""
    
    @staticmethod
    async def get_project_list(
        db: AsyncSession,
        page: int,
        page_size: int,
        query_params: ProjectQueryParams
    ) -> Tuple[List[ProjectBasicResponse], int]:
        """
        获取项目列表（分页）
        
        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            query_params: 查询参数
        
        Returns:
            (项目列表, 总数)
        """
        projects, total = await ProjectCRUD.get_list_paginated(
            db=db,
            page=page,
            page_size=page_size,
            project_type=query_params.project_type,
            formulator=query_params.formulator,
            date_start=query_params.date_start,
            date_end=query_params.date_end,
            keyword=query_params.keyword,
            has_compositions=query_params.has_compositions,
            has_test_results=query_params.has_test_results
        )
        
        # 转换为响应模型
        project_list = []
        for project in projects:
            # 手动构建响应数据，包含关联的类型名称
            project_data = ProjectBasicResponse.model_validate(project)
            # 如果有关联的项目类型，添加类型名称
            if project.project_type:
                project_data.TypeName = project.project_type.TypeName
            project_list.append(project_data)
        
        logger.info(f"queryproject列表successful: page{page}, per page{page_size}items, total{total}items")
        return project_list, total
    
    @staticmethod
    async def get_project_detail(
        db: AsyncSession,
        project_id: int
    ) -> ProjectDetailResponse:
        """
        获取项目详情
        
        Args:
            db: 数据库会话
            project_id: 项目ID
        
        Returns:
            项目详情
        """
        project = await ProjectCRUD.get_by_id(db, project_id)
        
        if not project:
            raise RecordNotFoundException("Project", project_id)
        
        # 构建响应
        project_detail = ProjectDetailResponse.model_validate(project)
        
        # 添加类型名称
        if project.project_type:
            project_detail.TypeName = project.project_type.TypeName
        
        # 添加配方成分
        if project.compositions:
            project_detail.compositions = [
                CompositionResponse.model_validate(comp)
                for comp in project.compositions
            ]
        
        return project_detail
    
    @staticmethod
    async def create_project(
        db: AsyncSession,
        project_data: ProjectCreateRequest
    ) -> ProjectBasicResponse:
        """
        创建新项目
        
        Args:
            db: 数据库会话
            project_data: 项目数据
        
        Returns:
            创建的项目信息
        
        Raises:
            IntegrityConstraintException: 数据完整性约束违规（如外键不存在）
            DatabaseException: 数据库操作失败
        """
        try:
            project = await ProjectCRUD.create_project(
                db=db,
                project_name=project_data.project_name,
                project_type_fk=project_data.project_type_fk,
                formulator_name=project_data.formulator_name,
                formulation_date=project_data.formulation_date,
                substrate_application=project_data.substrate_application
            )
            
            await db.commit()
            await db.refresh(project)
            
            logger.info(f"projectcreatesuccessful: {project.ProjectName} ({project.FormulaCode})")
            
            # 获取完整信息（包含关联数据）
            project = await ProjectCRUD.get_by_id(db, project.ProjectID)
            response = ProjectBasicResponse.model_validate(project)
            if project.project_type:
                response.TypeName = project.project_type.TypeName
            
            return response
        
        except IntegrityError as e:
            await db.rollback()
            logger.warning(f"projectcreatefailed - 数据完整性error: {e}")
            raise IntegrityConstraintException(
                message="Referenced project type does not exist or data constraint violated"
            )
        except DataError as e:
            await db.rollback()
            logger.warning(f"projectcreatefailed - 数据格式error: {e}")
            raise ValidationException(
                message="Invalid data format for project creation"
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"projectcreatefailed - 未知error: {type(e).__name__}: {e}", exc_info=True)
            raise DatabaseException(
                message="Failed to create project due to database error"
            )
    
    @staticmethod
    async def update_project(
        db: AsyncSession,
        project_id: int,
        project_data: ProjectUpdateRequest
    ) -> ProjectBasicResponse:
        """
        更新项目信息
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            project_data: 更新数据
        
        Returns:
            更新后的项目信息
        """
        # 检查项目是否存在
        project = await ProjectCRUD.get_by_id(db, project_id)
        if not project:
            raise RecordNotFoundException("Project", project_id)
        
        # 构建更新字段
        update_data = {}
        if project_data.project_name is not None:
            update_data["ProjectName"] = project_data.project_name
        if project_data.project_type_fk is not None:
            update_data["ProjectType_FK"] = project_data.project_type_fk
        if project_data.substrate_application is not None:
            update_data["SubstrateApplication"] = project_data.substrate_application
        if project_data.formulator_name is not None:
            update_data["FormulatorName"] = project_data.formulator_name
        if project_data.formulation_date is not None:
            update_data["FormulationDate"] = project_data.formulation_date
        
        try:
            await ProjectCRUD.update_project(db, project_id, **update_data)
            await db.commit()
            
            logger.info(f"projectupdatesuccessful: ID {project_id}")
            
            # 返回更新后的信息
            project = await ProjectCRUD.get_by_id(db, project_id)
            response = ProjectBasicResponse.model_validate(project)
            if project.project_type:
                response.TypeName = project.project_type.TypeName
            
            return response
        
        except IntegrityError as e:
            await db.rollback()
            logger.warning(f"projectupdatefailed - 数据完整性error: {e}")
            raise IntegrityConstraintException(
                message="Referenced project type does not exist or data constraint violated"
            )
        except DataError as e:
            await db.rollback()
            logger.warning(f"projectupdatefailed - 数据格式error: {e}")
            raise ValidationException(
                message="Invalid data format for project update"
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"projectupdatefailed - 未知error: {type(e).__name__}: {e}", exc_info=True)
            raise DatabaseException(
                message="Failed to update project due to database error"
            )
    
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
        # 检查项目是否存在
        project = await ProjectCRUD.get_by_id(db, project_id)
        if not project:
            raise RecordNotFoundException("Project", project_id)
        
        try:
            await ProjectCRUD.delete_project(db, project_id)
            await db.commit()
            logger.info(f"projectdeletedsuccessful: ID {project_id}")
            return True
        except IntegrityError as e:
            await db.rollback()
            logger.warning(f"projectdeletedfailed - 数据完整性error（可能存在关联数据）: {e}")
            raise IntegrityConstraintException(
                message="Cannot delete project with existing associated data (compositions, test results, etc.)"
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"projectdeletedfailed - 未知error: {type(e).__name__}: {e}", exc_info=True)
            raise DatabaseException(
                message="Failed to delete project due to database error"
            )
    
    @staticmethod
    async def batch_delete_projects(
        db: AsyncSession,
        delete_data: BatchDeleteRequest
    ) -> int:
        """
        批量删除项目
        
        Args:
            db: 数据库会话
            delete_data: 删除数据（包含ID列表）
        
        Returns:
            删除的数量
        """
        try:
            count = await ProjectCRUD.batch_delete_projects(db, delete_data.ids)
            await db.commit()
            logger.info(f"batchdeletedprojectsuccessful: deleted{count}items")
            return count
        except IntegrityError as e:
            await db.rollback()
            logger.warning(f"batchdeletedprojectfailed - 数据完整性error（部分project存在关联数据）: {e}")
            raise IntegrityConstraintException(
                message="Cannot delete some projects with existing associated data"
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"batchdeletedprojectfailed - 未知error: {type(e).__name__}: {e}", exc_info=True)
            raise DatabaseException(
                message="Failed to batch delete projects due to database error"
            )
    
    @staticmethod
    async def get_project_types(
        db: AsyncSession
    ) -> List[ProjectTypeResponse]:
        """
        获取所有项目类型
        
        Args:
            db: 数据库会话
        
        Returns:
            项目类型列表
        """
        types = await ProjectTypeCRUD.get_all(db)
        return [ProjectTypeResponse.model_validate(t) for t in types]
    
    @staticmethod
    async def get_formulators(
        db: AsyncSession
    ) -> List[str]:
        """
        获取所有配方设计师列表
        
        Args:
            db: 数据库会话
        
        Returns:
            配方设计师列表
        """
        return await ProjectTypeCRUD.get_formulators(db)


class CompositionService:
    """配方成分服务类"""
    
    @staticmethod
    async def get_compositions_by_project(
        db: AsyncSession,
        project_id: int
    ) -> List[CompositionResponse]:
        """
        获取项目的所有配方成分
        
        Args:
            db: 数据库会话
            project_id: 项目ID
        
        Returns:
            配方成分列表
        """
        # 检查项目是否存在
        project = await ProjectCRUD.get_by_id(db, project_id)
        if not project:
            raise RecordNotFoundException("Project", project_id)
        
        compositions = await CompositionCRUD.get_by_project_id(db, project_id)
        result = []
        for c in compositions:
            comp_dict = CompositionResponse.model_validate(c).model_dump(mode='json')
            # 添加原料或填料名称
            if c.material:
                comp_dict['MaterialName'] = c.material.TradeName
            if c.filler:
                comp_dict['FillerName'] = c.filler.TradeName
            result.append(CompositionResponse(**comp_dict))
        return result
    
    @staticmethod
    async def create_composition(
        db: AsyncSession,
        composition_data: CompositionCreateRequest
    ) -> CompositionResponse:
        """
        创建配方成分
        
        Args:
            db: 数据库会话
            composition_data: 成分数据
        
        Returns:
            创建的成分信息
        """
        # 验证至少有一个成分ID
        if not composition_data.material_id and not composition_data.filler_id:
            raise ValidationException("At least one of material_id or filler_id must be provided")
        
        # 检查项目是否存在
        project = await ProjectCRUD.get_by_id(db, composition_data.project_id)
        if not project:
            raise RecordNotFoundException("Project", composition_data.project_id)
        
        try:
            composition = await CompositionCRUD.create_composition(
                db=db,
                project_id=composition_data.project_id,
                material_id=composition_data.material_id,
                filler_id=composition_data.filler_id,
                weight_percentage=float(composition_data.weight_percentage),
                addition_method=composition_data.addition_method,
                remarks=composition_data.remarks
            )
            
            await db.commit()
            logger.info(f"formula成分createsuccessful: projectID {composition_data.project_id}")
            
            return CompositionResponse.model_validate(composition)
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create composition: {e}")
            raise DatabaseException(f"Failed to create composition: {str(e)}")
    
    @staticmethod
    async def update_composition(
        db: AsyncSession,
        composition_id: int,
        composition_data: CompositionUpdateRequest
    ) -> CompositionResponse:
        """
        更新配方成分
        
        Args:
            db: 数据库会话
            composition_id: 成分ID
            composition_data: 更新数据
        
        Returns:
            更新后的成分信息
        """
        try:
            composition = await CompositionCRUD.update_composition(
                db=db,
                composition_id=composition_id,
                material_id=composition_data.material_id,
                filler_id=composition_data.filler_id,
                weight_percentage=float(composition_data.weight_percentage) if composition_data.weight_percentage else None,
                addition_method=composition_data.addition_method,
                remarks=composition_data.remarks
            )
            
            if not composition:
                raise RecordNotFoundException("Composition", composition_id)
            
            await db.commit()
            await db.refresh(composition)
            logger.info(f"formula成分updatesuccessful: ID {composition_id}")
            
            return CompositionResponse.model_validate(composition)
            
        except RecordNotFoundException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update composition: {e}")
            raise DatabaseException(f"Failed to update composition: {str(e)}")
    
    @staticmethod
    async def delete_composition(
        db: AsyncSession,
        composition_id: int
    ) -> bool:
        """
        删除配方成分
        
        Args:
            db: 数据库会话
            composition_id: 成分ID
        
        Returns:
            是否成功
        """
        try:
            success = await CompositionCRUD.delete_composition(db, composition_id)
            if not success:
                raise RecordNotFoundException("Composition", composition_id)
            
            await db.commit()
            logger.info(f"formula成分deletedsuccessful: ID {composition_id}")
            return True
            
        except RecordNotFoundException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete composition: {e}")
            raise DatabaseException(f"Failed to delete composition: {str(e)}")

