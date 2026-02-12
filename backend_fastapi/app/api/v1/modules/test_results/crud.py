# -*- coding: utf-8 -*-
"""
测试结果管理CRUD操作
"""

from typing import Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.projects.model import (
    TestResultInkModel,
    TestResultCoatingModel,
    TestResult3DPrintModel,
    TestResultCompositeModel
)
from app.core.logger import logger


class TestResultCRUD:
    """测试结果CRUD操作类"""
    
    # ==================== 喷墨 ====================
    
    @staticmethod
    async def get_ink_result(
        db: AsyncSession,
        project_id: int
    ) -> Optional[TestResultInkModel]:
        """获取喷墨测试结果"""
        try:
            stmt = select(TestResultInkModel).where(
                TestResultInkModel.ProjectID_FK == project_id
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"query喷墨testresultfailed: {e}")
            raise
    
    @staticmethod
    async def create_ink_result(
        db: AsyncSession,
        project_id: int,
        **kwargs
    ) -> TestResultInkModel:
        """创建喷墨测试结果"""
        try:
            result = TestResultInkModel(
                ProjectID_FK=project_id,
                **kwargs
            )
            db.add(result)
            await db.flush()
            await db.refresh(result)
            return result
        except Exception as e:
            logger.error(f"create喷墨testresultfailed: {e}")
            raise
    
    @staticmethod
    async def update_ink_result(
        db: AsyncSession,
        project_id: int,
        **kwargs
    ) -> bool:
        """更新喷墨测试结果"""
        try:
            result = await TestResultCRUD.get_ink_result(db, project_id)
            if not result:
                return False
            
            for key, value in kwargs.items():
                if hasattr(result, key):
                    setattr(result, key, value)
            
            await db.flush()
            return True
        except Exception as e:
            logger.error(f"update喷墨testresultfailed: {e}")
            raise
    
    # ==================== 涂层 ====================
    
    @staticmethod
    async def get_coating_result(
        db: AsyncSession,
        project_id: int
    ) -> Optional[TestResultCoatingModel]:
        """获取涂层测试结果"""
        try:
            stmt = select(TestResultCoatingModel).where(
                TestResultCoatingModel.ProjectID_FK == project_id
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"query涂层testresultfailed: {e}")
            raise
    
    @staticmethod
    async def create_coating_result(
        db: AsyncSession,
        project_id: int,
        **kwargs
    ) -> TestResultCoatingModel:
        """创建涂层测试结果"""
        try:
            result = TestResultCoatingModel(
                ProjectID_FK=project_id,
                **kwargs
            )
            db.add(result)
            await db.flush()
            await db.refresh(result)
            return result
        except Exception as e:
            logger.error(f"create涂层testresultfailed: {e}")
            raise
    
    @staticmethod
    async def update_coating_result(
        db: AsyncSession,
        project_id: int,
        **kwargs
    ) -> bool:
        """更新涂层测试结果"""
        try:
            result = await TestResultCRUD.get_coating_result(db, project_id)
            if not result:
                return False
            
            for key, value in kwargs.items():
                if hasattr(result, key):
                    setattr(result, key, value)
            
            await db.flush()
            return True
        except Exception as e:
            logger.error(f"update涂层testresultfailed: {e}")
            raise
    
    # ==================== 3D打印 ====================
    
    @staticmethod
    async def get_3dprint_result(
        db: AsyncSession,
        project_id: int
    ) -> Optional[TestResult3DPrintModel]:
        """获取3D打印测试结果"""
        try:
            stmt = select(TestResult3DPrintModel).where(
                TestResult3DPrintModel.ProjectID_FK == project_id
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"query3D打印testresultfailed: {e}")
            raise
    
    @staticmethod
    async def create_3dprint_result(
        db: AsyncSession,
        project_id: int,
        **kwargs
    ) -> TestResult3DPrintModel:
        """创建3D打印测试结果"""
        try:
            result = TestResult3DPrintModel(
                ProjectID_FK=project_id,
                **kwargs
            )
            db.add(result)
            await db.flush()
            await db.refresh(result)
            return result
        except Exception as e:
            logger.error(f"create3D打印testresultfailed: {e}")
            raise
    
    @staticmethod
    async def update_3dprint_result(
        db: AsyncSession,
        project_id: int,
        **kwargs
    ) -> bool:
        """更新3D打印测试结果"""
        try:
            result = await TestResultCRUD.get_3dprint_result(db, project_id)
            if not result:
                return False
            
            for key, value in kwargs.items():
                if hasattr(result, key):
                    setattr(result, key, value)
            
            await db.flush()
            return True
        except Exception as e:
            logger.error(f"update3D打印testresultfailed: {e}")
            raise
    
    # ==================== 复合材料 ====================
    
    @staticmethod
    async def get_composite_result(
        db: AsyncSession,
        project_id: int
    ) -> Optional[TestResultCompositeModel]:
        """获取复合材料测试结果"""
        try:
            stmt = select(TestResultCompositeModel).where(
                TestResultCompositeModel.ProjectID_FK == project_id
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"query复合材料testresultfailed: {e}")
            raise
    
    @staticmethod
    async def create_composite_result(
        db: AsyncSession,
        project_id: int,
        **kwargs
    ) -> TestResultCompositeModel:
        """创建复合材料测试结果"""
        try:
            result = TestResultCompositeModel(
                ProjectID_FK=project_id,
                **kwargs
            )
            db.add(result)
            await db.flush()
            await db.refresh(result)
            return result
        except Exception as e:
            logger.error(f"create复合材料testresultfailed: {e}")
            raise
    
    @staticmethod
    async def update_composite_result(
        db: AsyncSession,
        project_id: int,
        **kwargs
    ) -> bool:
        """更新复合材料测试结果"""
        try:
            result = await TestResultCRUD.get_composite_result(db, project_id)
            if not result:
                return False
            
            for key, value in kwargs.items():
                if hasattr(result, key):
                    setattr(result, key, value)
            
            await db.flush()
            return True
        except Exception as e:
            logger.error(f"update复合材料testresultfailed: {e}")
            raise
    
    # ==================== 通用方法 ====================
    
    @staticmethod
    async def get_result_by_project_type(
        db: AsyncSession,
        project_id: int,
        project_type: str
    ) -> Optional[Union[TestResultInkModel, TestResultCoatingModel, TestResult3DPrintModel, TestResultCompositeModel]]:
        """根据项目类型获取测试结果（支持中英文）"""
        if project_type in ["喷墨", "Inkjet"]:
            return await TestResultCRUD.get_ink_result(db, project_id)
        elif project_type in ["涂层", "Coating"]:
            return await TestResultCRUD.get_coating_result(db, project_id)
        elif project_type in ["3D打印", "3D Printing"]:
            return await TestResultCRUD.get_3dprint_result(db, project_id)
        elif project_type in ["复合材料", "Composite"]:
            return await TestResultCRUD.get_composite_result(db, project_id)
        else:
            return None

