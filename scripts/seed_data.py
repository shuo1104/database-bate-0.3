import mysql.connector
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def seed_project_types(cursor):
    """Seeds the project types configuration table."""
    logger.info("开始导入项目类型数据...")
    
    # Check if data already exists to prevent duplicates
    cursor.execute("SELECT COUNT(*) FROM tbl_Config_ProjectTypes")
    if cursor.fetchone()[0] > 0:
        logger.info("项目类型表已有数据，跳过。")
        return

    project_types = [
        ('喷墨', 'INK'),
        ('涂层', 'COAT'),
        ('3D打印', '3D'),
        ('复合材料', 'COMP')
    ]
    
    sql = "INSERT INTO tbl_Config_ProjectTypes (TypeName, TypeCode) VALUES (%s, %s)"
    cursor.executemany(sql, project_types)
    logger.info(f"✓ 成功添加 {cursor.rowcount} 个项目类型。")

def seed_material_categories(cursor):
    """Seeds the material categories configuration table."""
    logger.info("开始导入材料类别数据...")

    cursor.execute("SELECT COUNT(*) FROM tbl_Config_MaterialCategories")
    if cursor.fetchone()[0] > 0:
        logger.info("材料类别表已有数据，跳过。")
        return
        
    categories = [
        ('单体',),
        ('低聚物',),
        ('光引发剂',),
        ('添加剂',),
        ('颜料',),
        ('溶剂',)
    ]
    
    sql = "INSERT INTO tbl_Config_MaterialCategories (CategoryName) VALUES (%s)"
    cursor.executemany(sql, categories)
    logger.info(f"✓ 成功添加 {cursor.rowcount} 个材料类别。")

def seed_filler_types(cursor):
    """Seeds the filler types configuration table."""
    logger.info("开始导入填料类型数据...")

    cursor.execute("SELECT COUNT(*) FROM tbl_Config_FillerTypes")
    if cursor.fetchone()[0] > 0:
        logger.info("填料类型表已有数据，跳过。")
        return
        
    filler_types = [
        ('玻璃',),
        ('二氧化硅',),
        ('二氧化锆',)
    ]
    
    sql = "INSERT INTO tbl_Config_FillerTypes (FillerTypeName) VALUES (%s)"
    cursor.executemany(sql, filler_types)
    logger.info(f"✓ 成功添加 {cursor.rowcount} 个填料类型。")


def main():
    """主函数：导入所有初始配置数据"""
    try:
        cnx = mysql.connector.connect(**config.DB_CONFIG)
        cursor = cnx.cursor()
        logger.info("数据库连接成功。")
        
        seed_project_types(cursor)
        seed_material_categories(cursor)
        seed_filler_types(cursor)
        
        cnx.commit()
        logger.info("\n✓ 所有初始数据导入完成。")

    except mysql.connector.Error as err:
        logger.error(f"发生错误: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()
            logger.info("MySQL 连接已关闭。")

if __name__ == "__main__":
    main()
