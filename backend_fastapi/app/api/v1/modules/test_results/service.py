# -*- coding: utf-8 -*-
"""
测试结果管理Service
"""

from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.test_results.crud import TestResultCRUD
from app.api.v1.modules.test_results.schema import (
    TestResultInkRequest, TestResultInkResponse,
    TestResultCoatingRequest, TestResultCoatingResponse,
    TestResult3DPrintRequest, TestResult3DPrintResponse,
    TestResultCompositeRequest, TestResultCompositeResponse
)
from app.api.v1.modules.projects.crud import ProjectCRUD
from app.core.logger import logger
from app.core.custom_exceptions import (
    RecordNotFoundException,
    DatabaseException,
)


class TestResultService:
    """测试结果服务类"""
    
    @staticmethod
    async def get_test_result(
        db: AsyncSession,
        project_id: int
    ) -> Union[TestResultInkResponse, TestResultCoatingResponse, TestResult3DPrintResponse, TestResultCompositeResponse, None]:
        """获取测试结果（根据项目类型自动判断）"""
        # 先获取项目信息确定项目类型
        project = await ProjectCRUD.get_by_id(db, project_id)
        if not project:
            raise RecordNotFoundException("Project", project_id)
        
        project_type = project.project_type.TypeName if project.project_type else None
        
        if not project_type:
            return None
        
        # 根据项目类型获取对应的测试结果
        result = await TestResultCRUD.get_result_by_project_type(db, project_id, project_type)
        
        if not result:
            return None
        
        # 转换为响应模型（支持中英文项目类型）
        if project_type in ["喷墨", "Inkjet"]:
            return TestResultInkResponse.model_validate(result)
        elif project_type in ["涂层", "Coating"]:
            return TestResultCoatingResponse.model_validate(result)
        elif project_type in ["3D打印", "3D Printing"]:
            return TestResult3DPrintResponse.model_validate(result)
        elif project_type in ["复合材料", "Composite"]:
            return TestResultCompositeResponse.model_validate(result)
        
        return None
    
    @staticmethod
    async def create_or_update_ink_result(
        db: AsyncSession,
        project_id: int,
        test_data: TestResultInkRequest
    ) -> TestResultInkResponse:
        """创建或更新喷墨测试结果"""
        # 检查项目是否存在
        project = await ProjectCRUD.get_by_id(db, project_id)
        if not project:
            raise RecordNotFoundException("Project", project_id)
        
        # 检查是否已存在测试结果
        existing = await TestResultCRUD.get_ink_result(db, project_id)
        
        try:
            if existing:
                # 更新
                update_data = test_data.model_dump(exclude_unset=True)
                await TestResultCRUD.update_ink_result(db, project_id, **update_data)
                await db.commit()
                result = await TestResultCRUD.get_ink_result(db, project_id)
            else:
                # 创建
                create_data = test_data.model_dump()
                result = await TestResultCRUD.create_ink_result(db, project_id, **create_data)
                await db.commit()
            
            logger.info(f"喷墨testresult{'update' if existing else 'create'}successful: projectID {project_id}")
            return TestResultInkResponse.model_validate(result)
            
        except RecordNotFoundException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to operate ink test result: {e}")
            raise DatabaseException(f"Failed to operate test result: {str(e)}")
    
    @staticmethod
    async def create_or_update_coating_result(
        db: AsyncSession,
        project_id: int,
        test_data: TestResultCoatingRequest
    ) -> TestResultCoatingResponse:
        """创建或更新涂层测试结果"""
        project = await ProjectCRUD.get_by_id(db, project_id)
        if not project:
            raise RecordNotFoundException("Project", project_id)
        
        existing = await TestResultCRUD.get_coating_result(db, project_id)
        
        try:
            if existing:
                update_data = test_data.model_dump(exclude_unset=True)
                await TestResultCRUD.update_coating_result(db, project_id, **update_data)
                await db.commit()
                result = await TestResultCRUD.get_coating_result(db, project_id)
            else:
                create_data = test_data.model_dump()
                result = await TestResultCRUD.create_coating_result(db, project_id, **create_data)
                await db.commit()
            
            logger.info(f"涂层testresult{'update' if existing else 'create'}successful: projectID {project_id}")
            return TestResultCoatingResponse.model_validate(result)
            
        except RecordNotFoundException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to operate coating test result: {e}")
            raise DatabaseException(f"Failed to operate test result: {str(e)}")
    
    @staticmethod
    async def create_or_update_3dprint_result(
        db: AsyncSession,
        project_id: int,
        test_data: TestResult3DPrintRequest
    ) -> TestResult3DPrintResponse:
        """创建或更新3D打印测试结果"""
        project = await ProjectCRUD.get_by_id(db, project_id)
        if not project:
            raise RecordNotFoundException("Project", project_id)
        
        existing = await TestResultCRUD.get_3dprint_result(db, project_id)
        
        try:
            if existing:
                update_data = test_data.model_dump(exclude_unset=True)
                await TestResultCRUD.update_3dprint_result(db, project_id, **update_data)
                await db.commit()
                result = await TestResultCRUD.get_3dprint_result(db, project_id)
            else:
                create_data = test_data.model_dump()
                result = await TestResultCRUD.create_3dprint_result(db, project_id, **create_data)
                await db.commit()
            
            logger.info(f"3D打印testresult{'update' if existing else 'create'}successful: projectID {project_id}")
            return TestResult3DPrintResponse.model_validate(result)
            
        except RecordNotFoundException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to operate 3D printing test result: {e}")
            raise DatabaseException(f"Failed to operate test result: {str(e)}")
    
    @staticmethod
    async def create_or_update_composite_result(
        db: AsyncSession,
        project_id: int,
        test_data: TestResultCompositeRequest
    ) -> TestResultCompositeResponse:
        """创建或更新复合材料测试结果"""
        project = await ProjectCRUD.get_by_id(db, project_id)
        if not project:
            raise RecordNotFoundException("Project", project_id)
        
        existing = await TestResultCRUD.get_composite_result(db, project_id)
        
        try:
            if existing:
                update_data = test_data.model_dump(exclude_unset=True)
                await TestResultCRUD.update_composite_result(db, project_id, **update_data)
                await db.commit()
                result = await TestResultCRUD.get_composite_result(db, project_id)
            else:
                create_data = test_data.model_dump()
                result = await TestResultCRUD.create_composite_result(db, project_id, **create_data)
                await db.commit()
            
            logger.info(f"复合材料testresult{'update' if existing else 'create'}successful: projectID {project_id}")
            return TestResultCompositeResponse.model_validate(result)
            
        except RecordNotFoundException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to operate composite test result: {e}")
            raise DatabaseException(f"Failed to operate test result: {str(e)}")

