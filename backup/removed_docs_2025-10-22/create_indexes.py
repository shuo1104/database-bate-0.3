#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""立即创建数据库索引"""

import mysql.connector
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import config

def create_indexes():
    """创建所有性能索引"""
    
    indexes = [
        # 项目信息表索引
        "CREATE INDEX IF NOT EXISTS idx_project_type_fk ON tbl_ProjectInfo(ProjectType_FK)",
        "CREATE INDEX IF NOT EXISTS idx_project_formulation_date ON tbl_ProjectInfo(FormulationDate)",
        "CREATE INDEX IF NOT EXISTS idx_project_formulator ON tbl_ProjectInfo(FormulatorName)",
        "CREATE INDEX IF NOT EXISTS idx_project_type_date ON tbl_ProjectInfo(ProjectType_FK, FormulationDate)",
        
        # 原料表索引
        "CREATE INDEX IF NOT EXISTS idx_material_category_fk ON tbl_RawMaterials(Category_FK)",
        "CREATE INDEX IF NOT EXISTS idx_material_supplier ON tbl_RawMaterials(Supplier)",
        "CREATE INDEX IF NOT EXISTS idx_material_cas ON tbl_RawMaterials(CAS_Number)",
        "CREATE INDEX IF NOT EXISTS idx_material_trade_name ON tbl_RawMaterials(TradeName)",
        
        # 无机填料表索引
        "CREATE INDEX IF NOT EXISTS idx_filler_type_fk ON tbl_InorganicFillers(FillerType_FK)",
        "CREATE INDEX IF NOT EXISTS idx_filler_supplier ON tbl_InorganicFillers(Supplier)",
        "CREATE INDEX IF NOT EXISTS idx_filler_trade_name ON tbl_InorganicFillers(TradeName)",
        "CREATE INDEX IF NOT EXISTS idx_filler_silanized ON tbl_InorganicFillers(IsSilanized)",
        
        # 配方成分表索引（非常重要！）
        "CREATE INDEX IF NOT EXISTS idx_composition_project_fk ON tbl_FormulaComposition(ProjectID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_composition_material_fk ON tbl_FormulaComposition(MaterialID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_composition_filler_fk ON tbl_FormulaComposition(FillerID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_composition_project_material ON tbl_FormulaComposition(ProjectID_FK, MaterialID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_composition_project_filler ON tbl_FormulaComposition(ProjectID_FK, FillerID_FK)",
        
        # 测试结果表索引
        "CREATE INDEX IF NOT EXISTS idx_test_ink_project_fk ON tbl_TestResults_Ink(ProjectID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_test_coating_project_fk ON tbl_TestResults_Coating(ProjectID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_test_3d_project_fk ON tbl_TestResults_3DPrint(ProjectID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_test_composite_project_fk ON tbl_TestResults_Composite(ProjectID_FK)",
        
        # 用户表索引
        "CREATE INDEX IF NOT EXISTS idx_users_role ON tbl_Users(Role)",
        "CREATE INDEX IF NOT EXISTS idx_users_is_active ON tbl_Users(IsActive)",
    ]
    
    try:
        print("连接数据库...")
        cnx = mysql.connector.connect(**config.DB_CONFIG)
        cursor = cnx.cursor()
        print(f"✓ 成功连接到数据库: {config.DB_CONFIG.get('database')}")
        
        print("\n开始创建索引...")
        created = 0
        skipped = 0
        
        for idx, index_sql in enumerate(indexes, 1):
            try:
                # 提取索引名称
                idx_name = index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else f'index_{idx}'
                print(f"[{idx}/{len(indexes)}] 创建 idx_{idx_name}...", end=' ')
                
                cursor.execute(index_sql)
                print("✓")
                created += 1
                
            except mysql.connector.Error as err:
                if err.errno == 1061:  # Duplicate key name
                    print("(已存在)")
                    skipped += 1
                else:
                    print(f"✗ 错误: {err}")
        
        cnx.commit()
        
        print(f"\n{'='*50}")
        print(f"✓ 索引创建完成！")
        print(f"  - 新创建: {created} 个")
        print(f"  - 已存在: {skipped} 个")
        print(f"  - 总计: {len(indexes)} 个")
        print(f"{'='*50}\n")
        
        # 验证索引
        print("验证索引...")
        cursor.execute("""
            SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = %s AND INDEX_NAME LIKE 'idx_%%'
            ORDER BY TABLE_NAME, INDEX_NAME
        """, (config.DB_CONFIG.get('database'),))
        
        results = cursor.fetchall()
        print(f"✓ 找到 {len(results)} 个索引")
        
        cursor.close()
        cnx.close()
        
        print("\n✓ 完成！数据库查询速度应该显著提升！")
        print("请刷新浏览器测试页面加载速度。\n")
        
        return True
        
    except mysql.connector.Error as err:
        print(f"\n✗ 数据库错误: {err}")
        return False
    except Exception as e:
        print(f"\n✗ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*50)
    print("  数据库索引创建工具")
    print("="*50)
    print()
    
    success = create_indexes()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

