# -*- coding: utf-8 -*-
"""
原料管理Service
"""

from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.materials.crud import MaterialCRUD, MaterialCategoryCRUD
from app.api.v1.modules.materials.schema import (
    MaterialCreateRequest,
    MaterialUpdateRequest,
    MaterialQueryParams,
    MaterialResponse,
    MaterialCategoryResponse,
    BatchDeleteRequest
)
from app.core.logger import logger
from app.core.custom_exceptions import (
    RecordNotFoundException,
    DatabaseException,
    IntegrityConstraintException,
)


class MaterialService:
    """原料服务类"""
    
    @staticmethod
    async def get_material_list(
        db: AsyncSession,
        page: int,
        page_size: int,
        query_params: MaterialQueryParams
    ) -> Tuple[List[MaterialResponse], int]:
        """获取原料列表（分页）"""
        materials, total = await MaterialCRUD.get_list_paginated(
            db=db,
            page=page,
            page_size=page_size,
            category=query_params.category,
            supplier=query_params.supplier,
            keyword=query_params.keyword
        )
        
        # 转换为响应模型
        material_list = []
        for material in materials:
            material_data = MaterialResponse.model_validate(material)
            if material.category:
                material_data.CategoryName = material.category.CategoryName
            material_list.append(material_data)
        
        logger.info(f"querymaterial列表successful: page{page}, total{total}items")
        return material_list, total
    
    @staticmethod
    async def get_material_detail(
        db: AsyncSession,
        material_id: int
    ) -> MaterialResponse:
        """获取原料详情"""
        material = await MaterialCRUD.get_by_id(db, material_id)
        
        if not material:
            raise RecordNotFoundException("Material", material_id)
        
        material_data = MaterialResponse.model_validate(material)
        if material.category:
            material_data.CategoryName = material.category.CategoryName
        
        return material_data
    
    @staticmethod
    async def create_material(
        db: AsyncSession,
        material_data: MaterialCreateRequest
    ) -> MaterialResponse:
        """创建新原料"""
        try:
            material = await MaterialCRUD.create_material(
                db=db,
                trade_name=material_data.trade_name,
                category_fk=material_data.category_fk,
                supplier=material_data.supplier,
                cas_number=material_data.cas_number,
                density=float(material_data.density) if material_data.density else None,
                viscosity=float(material_data.viscosity) if material_data.viscosity else None,
                function_description=material_data.function_description
            )
            
            await db.commit()
            await db.refresh(material)
            
            logger.info(f"materialcreatesuccessful: {material.TradeName}")
            
            material = await MaterialCRUD.get_by_id(db, material.MaterialID)
            response = MaterialResponse.model_validate(material)
            if material.category:
                response.CategoryName = material.category.CategoryName
            
            return response
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create material: {e}")
            raise DatabaseException(f"Failed to create material: {str(e)}")
    
    @staticmethod
    async def update_material(
        db: AsyncSession,
        material_id: int,
        material_data: MaterialUpdateRequest
    ) -> MaterialResponse:
        """更新原料信息"""
        # 检查原料是否存在
        material = await MaterialCRUD.get_by_id(db, material_id)
        if not material:
            raise RecordNotFoundException("Material", material_id)
        
        # 构建更新字段
        update_data = {}
        if material_data.trade_name is not None:
            update_data["TradeName"] = material_data.trade_name
        if material_data.category_fk is not None:
            update_data["Category_FK"] = material_data.category_fk
        if material_data.supplier is not None:
            update_data["Supplier"] = material_data.supplier
        if material_data.cas_number is not None:
            update_data["CAS_Number"] = material_data.cas_number
        if material_data.density is not None:
            update_data["Density"] = float(material_data.density)
        if material_data.viscosity is not None:
            update_data["Viscosity"] = float(material_data.viscosity)
        if material_data.function_description is not None:
            update_data["FunctionDescription"] = material_data.function_description
        
        try:
            await MaterialCRUD.update_material(db, material_id, **update_data)
            await db.commit()
            
            logger.info(f"materialupdatesuccessful: ID {material_id}")
            
            material = await MaterialCRUD.get_by_id(db, material_id)
            response = MaterialResponse.model_validate(material)
            if material.category:
                response.CategoryName = material.category.CategoryName
            
            return response
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update material: {e}")
            raise DatabaseException(f"Failed to update material: {str(e)}")
    
    @staticmethod
    async def delete_material(
        db: AsyncSession,
        material_id: int
    ) -> bool:
        """删除原料"""
        material = await MaterialCRUD.get_by_id(db, material_id)
        if not material:
            raise RecordNotFoundException("Material", material_id)
        
        try:
            await MaterialCRUD.delete_material(db, material_id)
            await db.commit()
            logger.info(f"materialdeletedsuccessful: ID {material_id}")
            return True
        except RecordNotFoundException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete material: {e}")
            raise DatabaseException(f"Failed to delete material: {str(e)}")
    
    @staticmethod
    async def batch_delete_materials(
        db: AsyncSession,
        delete_data: BatchDeleteRequest
    ) -> int:
        """批量删除原料"""
        try:
            count = await MaterialCRUD.batch_delete_materials(db, delete_data.ids)
            await db.commit()
            logger.info(f"batchdeletedmaterialsuccessful: deleted{count}items")
            return count
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to batch delete materials: {e}")
            raise DatabaseException(f"Failed to batch delete materials: {str(e)}")
    
    @staticmethod
    async def get_categories(
        db: AsyncSession
    ) -> List[MaterialCategoryResponse]:
        """获取所有原料类别"""
        categories = await MaterialCategoryCRUD.get_all(db)
        return [MaterialCategoryResponse.model_validate(c) for c in categories]
    
    @staticmethod
    async def get_suppliers(
        db: AsyncSession
    ) -> List[str]:
        """获取所有供应商列表"""
        return await MaterialCategoryCRUD.get_suppliers(db)

