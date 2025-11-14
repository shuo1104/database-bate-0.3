# -*- coding: utf-8 -*-
"""
填料管理Service
"""

from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.fillers.crud import FillerCRUD, FillerTypeCRUD
from app.api.v1.modules.fillers.schema import (
    FillerCreateRequest,
    FillerUpdateRequest,
    FillerQueryParams,
    FillerResponse,
    FillerTypeResponse,
    BatchDeleteRequest
)
from app.core.logger import logger
from app.core.custom_exceptions import (
    RecordNotFoundException,
    DatabaseException,
    IntegrityConstraintException,
)


class FillerService:
    """填料服务类"""
    
    @staticmethod
    async def get_filler_list(
        db: AsyncSession,
        page: int,
        page_size: int,
        query_params: FillerQueryParams
    ) -> Tuple[List[FillerResponse], int]:
        """获取填料列表（分页）"""
        fillers, total = await FillerCRUD.get_list_paginated(
            db=db,
            page=page,
            page_size=page_size,
            filler_type=query_params.filler_type,
            supplier=query_params.supplier,
            keyword=query_params.keyword
        )
        
        # 转换为响应模型
        filler_list = []
        for filler in fillers:
            filler_data = FillerResponse.model_validate(filler)
            if filler.filler_type:
                filler_data.FillerTypeName = filler.filler_type.FillerTypeName
            filler_list.append(filler_data)
        
        logger.info(f"queryfiller列表successful: page{page}, total{total}items")
        return filler_list, total
    
    @staticmethod
    async def get_filler_detail(
        db: AsyncSession,
        filler_id: int
    ) -> FillerResponse:
        """获取填料详情"""
        filler = await FillerCRUD.get_by_id(db, filler_id)
        
        if not filler:
            raise RecordNotFoundException("Filler", filler_id)
        
        filler_data = FillerResponse.model_validate(filler)
        if filler.filler_type:
            filler_data.FillerTypeName = filler.filler_type.FillerTypeName
        
        return filler_data
    
    @staticmethod
    async def create_filler(
        db: AsyncSession,
        filler_data: FillerCreateRequest
    ) -> FillerResponse:
        """创建新填料"""
        try:
            filler = await FillerCRUD.create_filler(
                db=db,
                trade_name=filler_data.trade_name,
                filler_type_fk=filler_data.filler_type_fk,
                supplier=filler_data.supplier,
                particle_size=filler_data.particle_size,
                is_silanized=filler_data.is_silanized,
                coupling_agent=filler_data.coupling_agent,
                surface_area=float(filler_data.surface_area) if filler_data.surface_area else None
            )
            
            await db.commit()
            await db.refresh(filler)
            
            logger.info(f"fillercreatesuccessful: {filler.TradeName}")
            
            filler = await FillerCRUD.get_by_id(db, filler.FillerID)
            response = FillerResponse.model_validate(filler)
            if filler.filler_type:
                response.FillerTypeName = filler.filler_type.FillerTypeName
            
            return response
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create filler: {e}")
            raise DatabaseException(f"Failed to create filler: {str(e)}")
    
    @staticmethod
    async def update_filler(
        db: AsyncSession,
        filler_id: int,
        filler_data: FillerUpdateRequest
    ) -> FillerResponse:
        """更新填料信息"""
        # 检查填料是否存在
        filler = await FillerCRUD.get_by_id(db, filler_id)
        if not filler:
            raise RecordNotFoundException("Filler", filler_id)
        
        # 构建更新字段
        update_data = {}
        if filler_data.trade_name is not None:
            update_data["TradeName"] = filler_data.trade_name
        if filler_data.filler_type_fk is not None:
            update_data["FillerType_FK"] = filler_data.filler_type_fk
        if filler_data.supplier is not None:
            update_data["Supplier"] = filler_data.supplier
        if filler_data.particle_size is not None:
            update_data["ParticleSize"] = filler_data.particle_size
        if filler_data.is_silanized is not None:
            update_data["IsSilanized"] = filler_data.is_silanized
        if filler_data.coupling_agent is not None:
            update_data["CouplingAgent"] = filler_data.coupling_agent
        if filler_data.surface_area is not None:
            update_data["SurfaceArea"] = float(filler_data.surface_area)
        
        try:
            await FillerCRUD.update_filler(db, filler_id, **update_data)
            await db.commit()
            
            logger.info(f"fillerupdatesuccessful: ID {filler_id}")
            
            filler = await FillerCRUD.get_by_id(db, filler_id)
            response = FillerResponse.model_validate(filler)
            if filler.filler_type:
                response.FillerTypeName = filler.filler_type.FillerTypeName
            
            return response
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update filler: {e}")
            raise DatabaseException(f"Failed to update filler: {str(e)}")
    
    @staticmethod
    async def delete_filler(
        db: AsyncSession,
        filler_id: int
    ) -> bool:
        """删除填料"""
        filler = await FillerCRUD.get_by_id(db, filler_id)
        if not filler:
            raise RecordNotFoundException("Filler", filler_id)
        
        try:
            await FillerCRUD.delete_filler(db, filler_id)
            await db.commit()
            logger.info(f"fillerdeletedsuccessful: ID {filler_id}")
            return True
        except RecordNotFoundException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete filler: {e}")
            raise DatabaseException(f"Failed to delete filler: {str(e)}")
    
    @staticmethod
    async def batch_delete_fillers(
        db: AsyncSession,
        delete_data: BatchDeleteRequest
    ) -> int:
        """批量删除填料"""
        try:
            count = await FillerCRUD.batch_delete_fillers(db, delete_data.ids)
            await db.commit()
            logger.info(f"batchdeletedfillersuccessful: deleted{count}items")
            return count
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to batch delete fillers: {e}")
            raise DatabaseException(f"Failed to batch delete fillers: {str(e)}")
    
    @staticmethod
    async def get_filler_types(
        db: AsyncSession
    ) -> List[FillerTypeResponse]:
        """获取所有填料类型"""
        types = await FillerTypeCRUD.get_all(db)
        return [FillerTypeResponse.model_validate(t) for t in types]
    
    @staticmethod
    async def get_suppliers(
        db: AsyncSession
    ) -> List[str]:
        """获取所有供应商列表"""
        return await FillerTypeCRUD.get_suppliers(db)

