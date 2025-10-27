# -*- coding: utf-8 -*-
"""
原料管理CRUD操作
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.modules.materials.model import MaterialModel, MaterialCategoryModel
from app.core.logger import logger


class MaterialCRUD:
    """原料CRUD操作类"""
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        material_id: int
    ) -> Optional[MaterialModel]:
        """根据ID查询原料"""
        try:
            stmt = (
                select(MaterialModel)
                .options(selectinload(MaterialModel.category))
                .where(MaterialModel.MaterialID == material_id)
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"查询原料失败: {e}")
            raise
    
    @staticmethod
    async def get_list_paginated(
        db: AsyncSession,
        page: int,
        page_size: int,
        category: Optional[str] = None,
        supplier: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[MaterialModel], int]:
        """分页查询原料列表"""
        try:
            # 构建查询条件
            conditions = []
            
            if category:
                conditions.append(MaterialCategoryModel.CategoryName == category)
            
            if supplier:
                conditions.append(MaterialModel.Supplier == supplier)
            
            if keyword:
                conditions.append(
                    or_(
                        MaterialModel.TradeName.like(f"%{keyword}%"),
                        MaterialModel.CAS_Number.like(f"%{keyword}%")
                    )
                )
            
            # 查询总数
            count_stmt = (
                select(func.count(MaterialModel.MaterialID))
                .select_from(MaterialModel)
                .join(
                    MaterialCategoryModel,
                    MaterialModel.Category_FK == MaterialCategoryModel.CategoryID,
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
                select(MaterialModel)
                .options(selectinload(MaterialModel.category))
                .join(
                    MaterialCategoryModel,
                    MaterialModel.Category_FK == MaterialCategoryModel.CategoryID,
                    isouter=True
                )
                .order_by(MaterialModel.MaterialID.desc())
                .offset(offset)
                .limit(page_size)
            )
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            result = await db.execute(stmt)
            materials = result.scalars().all()
            
            return list(materials), total
            
        except Exception as e:
            logger.error(f"分页查询原料失败: {e}")
            raise
    
    @staticmethod
    async def create_material(
        db: AsyncSession,
        trade_name: str,
        category_fk: Optional[int] = None,
        supplier: Optional[str] = None,
        cas_number: Optional[str] = None,
        density: Optional[float] = None,
        viscosity: Optional[float] = None,
        function_description: Optional[str] = None
    ) -> MaterialModel:
        """创建新原料"""
        try:
            material = MaterialModel(
                TradeName=trade_name,
                Category_FK=category_fk,
                Supplier=supplier,
                CAS_Number=cas_number,
                Density=density,
                Viscosity=viscosity,
                FunctionDescription=function_description
            )
            
            db.add(material)
            await db.flush()
            await db.refresh(material)
            
            return material
            
        except Exception as e:
            logger.error(f"创建原料失败: {e}")
            raise
    
    @staticmethod
    async def update_material(
        db: AsyncSession,
        material_id: int,
        **kwargs
    ) -> bool:
        """更新原料信息"""
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return True
            
            stmt = (
                update(MaterialModel)
                .where(MaterialModel.MaterialID == material_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            
            return True
            
        except Exception as e:
            logger.error(f"更新原料失败: {e}")
            return False
    
    @staticmethod
    async def delete_material(
        db: AsyncSession,
        material_id: int
    ) -> bool:
        """删除原料"""
        try:
            stmt = delete(MaterialModel).where(MaterialModel.MaterialID == material_id)
            await db.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"删除原料失败: {e}")
            return False
    
    @staticmethod
    async def batch_delete_materials(
        db: AsyncSession,
        material_ids: List[int]
    ) -> int:
        """批量删除原料"""
        try:
            stmt = delete(MaterialModel).where(MaterialModel.MaterialID.in_(material_ids))
            result = await db.execute(stmt)
            return result.rowcount
        except Exception as e:
            logger.error(f"批量删除原料失败: {e}")
            raise


class MaterialCategoryCRUD:
    """原料类别CRUD操作类"""
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[MaterialCategoryModel]:
        """获取所有原料类别"""
        try:
            stmt = select(MaterialCategoryModel).order_by(MaterialCategoryModel.CategoryName)
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"查询原料类别失败: {e}")
            raise
    
    @staticmethod
    async def get_suppliers(db: AsyncSession) -> List[str]:
        """获取所有供应商列表（去重）"""
        try:
            stmt = (
                select(MaterialModel.Supplier)
                .where(MaterialModel.Supplier.isnot(None))
                .where(MaterialModel.Supplier != "")
                .distinct()
                .order_by(MaterialModel.Supplier)
            )
            result = await db.execute(stmt)
            return [row[0] for row in result.all()]
        except Exception as e:
            logger.error(f"查询供应商列表失败: {e}")
            raise

