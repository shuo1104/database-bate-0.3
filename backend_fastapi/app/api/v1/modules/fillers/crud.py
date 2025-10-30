# -*- coding: utf-8 -*-
"""
填料管理CRUD操作
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.modules.fillers.model import FillerModel, FillerTypeModel
from app.core.logger import logger


class FillerCRUD:
    """填料CRUD操作类"""
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        filler_id: int
    ) -> Optional[FillerModel]:
        """根据ID查询填料"""
        try:
            stmt = (
                select(FillerModel)
                .options(selectinload(FillerModel.filler_type))
                .where(FillerModel.FillerID == filler_id)
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"queryfillerfailed: {e}")
            raise
    
    @staticmethod
    async def get_list_paginated(
        db: AsyncSession,
        page: int,
        page_size: int,
        filler_type: Optional[str] = None,
        supplier: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[FillerModel], int]:
        """分页查询填料列表"""
        try:
            # 构建查询条件
            conditions = []
            
            if filler_type:
                conditions.append(FillerTypeModel.FillerTypeName == filler_type)
            
            if supplier:
                conditions.append(FillerModel.Supplier == supplier)
            
            if keyword:
                conditions.append(FillerModel.TradeName.like(f"%{keyword}%"))
            
            # 查询总数
            count_stmt = (
                select(func.count(FillerModel.FillerID))
                .select_from(FillerModel)
                .join(
                    FillerTypeModel,
                    FillerModel.FillerType_FK == FillerTypeModel.FillerTypeID,
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
                select(FillerModel)
                .options(selectinload(FillerModel.filler_type))
                .join(
                    FillerTypeModel,
                    FillerModel.FillerType_FK == FillerTypeModel.FillerTypeID,
                    isouter=True
                )
                .order_by(FillerModel.FillerID.desc())
                .offset(offset)
                .limit(page_size)
            )
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            result = await db.execute(stmt)
            fillers = result.scalars().all()
            
            return list(fillers), total
            
        except Exception as e:
            logger.error(f"分页queryfillerfailed: {e}")
            raise
    
    @staticmethod
    async def create_filler(
        db: AsyncSession,
        trade_name: str,
        filler_type_fk: Optional[int] = None,
        supplier: Optional[str] = None,
        particle_size: Optional[str] = None,
        is_silanized: Optional[int] = None,
        coupling_agent: Optional[str] = None,
        surface_area: Optional[float] = None
    ) -> FillerModel:
        """创建新填料"""
        try:
            filler = FillerModel(
                TradeName=trade_name,
                FillerType_FK=filler_type_fk,
                Supplier=supplier,
                ParticleSize=particle_size,
                IsSilanized=is_silanized,
                CouplingAgent=coupling_agent,
                SurfaceArea=surface_area
            )
            
            db.add(filler)
            await db.flush()
            await db.refresh(filler)
            
            return filler
            
        except Exception as e:
            logger.error(f"createfillerfailed: {e}")
            raise
    
    @staticmethod
    async def update_filler(
        db: AsyncSession,
        filler_id: int,
        **kwargs
    ) -> bool:
        """更新填料信息"""
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return True
            
            stmt = (
                update(FillerModel)
                .where(FillerModel.FillerID == filler_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            
            return True
            
        except Exception as e:
            logger.error(f"updatefillerfailed: {e}")
            return False
    
    @staticmethod
    async def delete_filler(
        db: AsyncSession,
        filler_id: int
    ) -> bool:
        """删除填料"""
        try:
            stmt = delete(FillerModel).where(FillerModel.FillerID == filler_id)
            await db.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"deletedfillerfailed: {e}")
            return False
    
    @staticmethod
    async def batch_delete_fillers(
        db: AsyncSession,
        filler_ids: List[int]
    ) -> int:
        """批量删除填料"""
        try:
            stmt = delete(FillerModel).where(FillerModel.FillerID.in_(filler_ids))
            result = await db.execute(stmt)
            return result.rowcount
        except Exception as e:
            logger.error(f"batchdeletedfillerfailed: {e}")
            raise


class FillerTypeCRUD:
    """填料类型CRUD操作类"""
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[FillerTypeModel]:
        """获取所有填料类型"""
        try:
            stmt = select(FillerTypeModel).order_by(FillerTypeModel.FillerTypeName)
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"queryfiller类型failed: {e}")
            raise
    
    @staticmethod
    async def get_suppliers(db: AsyncSession) -> List[str]:
        """获取所有供应商列表（去重）"""
        try:
            stmt = (
                select(FillerModel.Supplier)
                .where(FillerModel.Supplier.isnot(None))
                .where(FillerModel.Supplier != "")
                .distinct()
                .order_by(FillerModel.Supplier)
            )
            result = await db.execute(stmt)
            return [row[0] for row in result.all()]
        except Exception as e:
            logger.error(f"query供应商列表failed: {e}")
            raise

