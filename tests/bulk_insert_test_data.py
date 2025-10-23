"""
批量插入1000条测试数据脚本
用于测试数据库性能和系统负载能力
"""
import mysql.connector
import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ============================================
# 随机数据生成器
# ============================================

def random_date(start_year=2020, end_year=2025):
    """生成随机日期"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).date()

def random_decimal(min_val, max_val, decimals=4):
    """生成随机decimal值"""
    value = random.uniform(min_val, max_val)
    return round(Decimal(str(value)), decimals)

# 随机名称生成器
SUPPLIER_NAMES = [
    '巴斯夫', '陶氏化学', '帝斯曼', '科思创', '阿克苏诺贝尔',
    '赢创工业', '索尔维', '亨斯迈', '万华化学', '三棵树',
    '立邦', '多乐士', 'PPG工业', '艾仕得', '关西涂料',
    '日本油漆', '宣伟', 'RPM国际', '阿科玛', '瓦克化学'
]

FORMULATOR_NAMES = [
    '张伟', '李娜', '王强', '刘敏', '陈杰',
    '杨洋', '黄婷', '赵磊', '周芳', '吴刚',
    '徐静', '孙波', '马超', '朱丽', '胡鹏',
    '郭红', '林涛', '何军', '高燕', '梁晨'
]

MATERIAL_PREFIXES = [
    'HDDA', 'TPGDA', 'DPGDA', 'PEA', 'IBOA',
    'TMPTA', 'PETA', 'DPHA', 'SR', 'CN',
    'Ebecryl', 'Sartomer', 'Photomer', 'Laromer', 'Miramer'
]

FILLER_PREFIXES = [
    'SiO2', 'ZrO2', 'Glass', 'Aerosil', 'Cab-O-Sil',
    'Zeolite', 'Silica', 'Zirconia', 'Nano', 'Micro'
]

SUBSTRATES = [
    'PET薄膜', 'PC板材', '玻璃基材', '金属表面', '陶瓷基材',
    '木质材料', 'ABS塑料', '纸张', '纺织品', '皮革',
    '混凝土', '石材', 'PMMA', 'PP材料', 'PE材料'
]

# ============================================
# 数据插入函数
# ============================================

def ensure_config_data(cursor):
    """确保配置表有数据"""
    logger.info("检查配置表数据...")
    
    # 检查项目类型
    cursor.execute("SELECT COUNT(*) FROM tbl_Config_ProjectTypes")
    if cursor.fetchone()[0] == 0:
        project_types = [
            ('喷墨', 'INK'),
            ('涂层', 'COAT'),
            ('3D打印', '3D'),
            ('复合材料', 'COMP')
        ]
        cursor.executemany(
            "INSERT INTO tbl_Config_ProjectTypes (TypeName, TypeCode) VALUES (%s, %s)",
            project_types
        )
        logger.info("✓ 添加项目类型数据")
    
    # 检查材料类别
    cursor.execute("SELECT COUNT(*) FROM tbl_Config_MaterialCategories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ('单体',), ('低聚物',), ('光引发剂',),
            ('添加剂',), ('颜料',), ('溶剂',)
        ]
        cursor.executemany(
            "INSERT INTO tbl_Config_MaterialCategories (CategoryName) VALUES (%s)",
            categories
        )
        logger.info("✓ 添加材料类别数据")
    
    # 检查填料类型
    cursor.execute("SELECT COUNT(*) FROM tbl_Config_FillerTypes")
    if cursor.fetchone()[0] == 0:
        filler_types = [
            ('玻璃',), ('二氧化硅',), ('二氧化锆',)
        ]
        cursor.executemany(
            "INSERT INTO tbl_Config_FillerTypes (FillerTypeName) VALUES (%s)",
            filler_types
        )
        logger.info("✓ 添加填料类型数据")

def insert_projects(cursor, count=1000):
    """插入项目信息"""
    logger.info(f"开始插入 {count} 条项目数据...")
    
    # 获取项目类型ID
    cursor.execute("SELECT TypeID FROM tbl_Config_ProjectTypes")
    type_ids = [row[0] for row in cursor.fetchall()]
    
    projects = []
    for i in range(1, count + 1):
        project = (
            f'测试项目_{i:04d}',  # ProjectName
            random.choice(type_ids),  # ProjectType_FK
            random.choice(SUBSTRATES),  # SubstrateApplication
            random.choice(FORMULATOR_NAMES),  # FormulatorName
            random_date(),  # FormulationDate
            f'FORMULA-{i:06d}'  # FormulaCode
        )
        projects.append(project)
    
    sql = """
        INSERT INTO tbl_ProjectInfo 
        (ProjectName, ProjectType_FK, SubstrateApplication, FormulatorName, FormulationDate, FormulaCode)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(sql, projects)
    logger.info(f"✓ 成功插入 {cursor.rowcount} 条项目数据")

def insert_materials(cursor, count=500):
    """插入原料信息"""
    logger.info(f"开始插入 {count} 条原料数据...")
    
    # 获取材料类别ID
    cursor.execute("SELECT CategoryID FROM tbl_Config_MaterialCategories")
    category_ids = [row[0] for row in cursor.fetchall()]
    
    materials = []
    for i in range(1, count + 1):
        material = (
            f'{random.choice(MATERIAL_PREFIXES)}-{i:03d}',  # TradeName
            random.choice(category_ids),  # Category_FK
            random.choice(SUPPLIER_NAMES),  # Supplier
            f'{random.randint(100, 9999)}-{random.randint(10, 99)}-{random.randint(0, 9)}',  # CAS_Number
            random_decimal(0.8, 1.5),  # Density
            random_decimal(10, 5000),  # Viscosity
            f'功能说明_{i}'  # FunctionDescription
        )
        materials.append(material)
    
    sql = """
        INSERT INTO tbl_RawMaterials 
        (TradeName, Category_FK, Supplier, CAS_Number, Density, Viscosity, FunctionDescription)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(sql, materials)
    logger.info(f"✓ 成功插入 {cursor.rowcount} 条原料数据")

def insert_fillers(cursor, count=200):
    """插入无机填料信息"""
    logger.info(f"开始插入 {count} 条填料数据...")
    
    # 获取填料类型ID
    cursor.execute("SELECT FillerTypeID FROM tbl_Config_FillerTypes")
    filler_type_ids = [row[0] for row in cursor.fetchall()]
    
    fillers = []
    for i in range(1, count + 1):
        filler = (
            f'{random.choice(FILLER_PREFIXES)}-{i:03d}',  # TradeName
            random.choice(filler_type_ids),  # FillerType_FK
            random.choice(SUPPLIER_NAMES),  # Supplier
            f'D50: {random.randint(10, 500)}nm',  # ParticleSize
            random.choice([0, 1]),  # IsSilanized
            f'偶联剂_{random.randint(1, 10)}' if random.choice([True, False]) else None,  # CouplingAgent
            random_decimal(50, 500)  # SurfaceArea
        )
        fillers.append(filler)
    
    sql = """
        INSERT INTO tbl_InorganicFillers 
        (TradeName, FillerType_FK, Supplier, ParticleSize, IsSilanized, CouplingAgent, SurfaceArea)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(sql, fillers)
    logger.info(f"✓ 成功插入 {cursor.rowcount} 条填料数据")

def insert_formula_compositions(cursor, count=3000):
    """插入配方成分（每个项目约3个成分）"""
    logger.info(f"开始插入 {count} 条配方成分数据...")
    
    # 获取项目ID
    cursor.execute("SELECT ProjectID FROM tbl_ProjectInfo")
    project_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取原料ID
    cursor.execute("SELECT MaterialID FROM tbl_RawMaterials")
    material_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取填料ID
    cursor.execute("SELECT FillerID FROM tbl_InorganicFillers")
    filler_ids = [row[0] for row in cursor.fetchall()]
    
    compositions = []
    for _ in range(count):
        # 随机选择使用原料或填料
        use_material = random.choice([True, False])
        
        composition = (
            random.choice(project_ids),  # ProjectID_FK
            random.choice(material_ids) if use_material else None,  # MaterialID_FK
            None if use_material else random.choice(filler_ids),  # FillerID_FK
            random_decimal(0.1, 99.9, 4),  # WeightPercentage
            random.choice(['直接混合', '分散后添加', '预分散', '后期添加', '逐步加入']),  # AdditionMethod
            f'备注_{random.randint(1, 100)}' if random.random() > 0.5 else None  # Remarks
        )
        compositions.append(composition)
    
    sql = """
        INSERT INTO tbl_FormulaComposition 
        (ProjectID_FK, MaterialID_FK, FillerID_FK, WeightPercentage, AdditionMethod, Remarks)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(sql, compositions)
    logger.info(f"✓ 成功插入 {cursor.rowcount} 条配方成分数据")

def insert_test_results(cursor):
    """插入测试结果数据（根据项目类型）"""
    logger.info("开始插入测试结果数据...")
    
    # 获取所有项目及其类型
    cursor.execute("""
        SELECT p.ProjectID, t.TypeCode 
        FROM tbl_ProjectInfo p
        LEFT JOIN tbl_Config_ProjectTypes t ON p.ProjectType_FK = t.TypeID
    """)
    projects = cursor.fetchall()
    
    ink_count = coating_count = print3d_count = composite_count = 0
    
    for project_id, type_code in projects:
        test_date = random_date()
        
        if type_code == 'INK':
            # 喷墨测试结果
            try:
                cursor.execute("""
                    INSERT INTO tbl_TestResults_Ink 
                    (ProjectID_FK, Ink_Viscosity, Ink_Reactivity, Ink_ParticleSize, 
                     Ink_SurfaceTension, Ink_ColorValue, TestDate, Notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    project_id,
                    f'{random.randint(5, 50)} cPs',
                    f'{random.randint(1, 10)} 秒',
                    f'{random.randint(50, 500)} nm',
                    f'{random.randint(20, 50)} mN/m',
                    f'L*{random.randint(40, 80)} a*{random.randint(-20, 20)} b*{random.randint(-20, 20)}',
                    test_date,
                    f'测试备注_{random.randint(1, 100)}'
                ))
                ink_count += 1
            except mysql.connector.Error:
                pass  # 跳过已存在的记录
                
        elif type_code == 'COAT':
            # 涂层测试结果
            try:
                cursor.execute("""
                    INSERT INTO tbl_TestResults_Coating 
                    (ProjectID_FK, Coating_Adhesion, Coating_Transparency, Coating_SurfaceHardness,
                     Coating_ChemicalResistance, Coating_CostEstimate, TestDate, Notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    project_id,
                    f'{random.randint(0, 5)}B',
                    f'{random.randint(80, 99)}%',
                    f'{random.choice(["2H", "3H", "4H", "5H", "6H"])}',
                    random.choice(['优秀', '良好', '一般', '较差']),
                    f'{random_decimal(5, 50)} €/kg',
                    test_date,
                    f'测试备注_{random.randint(1, 100)}'
                ))
                coating_count += 1
            except mysql.connector.Error:
                pass
                
        elif type_code == '3D':
            # 3D打印测试结果
            try:
                cursor.execute("""
                    INSERT INTO tbl_TestResults_3DPrint 
                    (ProjectID_FK, Print3D_Shrinkage, Print3D_YoungsModulus, Print3D_FlexuralStrength,
                     Print3D_ShoreHardness, Print3D_ImpactResistance, TestDate, Notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    project_id,
                    f'{random_decimal(0.1, 5.0, 2)}%',
                    f'{random.randint(500, 5000)} MPa',
                    f'{random.randint(50, 200)} MPa',
                    f'{random.choice(["A", "D"])}{random.randint(60, 95)}',
                    f'{random.randint(10, 100)} kJ/m²',
                    test_date,
                    f'测试备注_{random.randint(1, 100)}'
                ))
                print3d_count += 1
            except mysql.connector.Error:
                pass
                
        elif type_code == 'COMP':
            # 复合材料测试结果
            try:
                cursor.execute("""
                    INSERT INTO tbl_TestResults_Composite 
                    (ProjectID_FK, Composite_FlexuralStrength, Composite_YoungsModulus,
                     Composite_ImpactResistance, Composite_ConversionRate, TestDate, Notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    project_id,
                    f'{random.randint(100, 300)} MPa',
                    f'{random.randint(1000, 10000)} MPa',
                    f'{random.randint(20, 150)} kJ/m²',
                    f'{random_decimal(85, 99, 2)}%',
                    test_date,
                    f'测试备注_{random.randint(1, 100)}'
                ))
                composite_count += 1
            except mysql.connector.Error:
                pass
    
    logger.info(f"✓ 成功插入测试结果数据：")
    logger.info(f"  - 喷墨: {ink_count} 条")
    logger.info(f"  - 涂层: {coating_count} 条")
    logger.info(f"  - 3D打印: {print3d_count} 条")
    logger.info(f"  - 复合材料: {composite_count} 条")

# ============================================
# 主函数
# ============================================

def main():
    """主函数：批量插入测试数据"""
    try:
        logger.info("=" * 60)
        logger.info("开始批量插入1000条测试数据")
        logger.info("=" * 60)
        
        # 连接数据库
        cnx = mysql.connector.connect(**config.DB_CONFIG)
        cursor = cnx.cursor()
        logger.info("✓ 数据库连接成功")
        
        # 确保配置表有数据
        ensure_config_data(cursor)
        cnx.commit()
        
        # 插入项目信息（1000条）
        insert_projects(cursor, count=1000)
        cnx.commit()
        
        # 插入原料信息（500条）
        insert_materials(cursor, count=500)
        cnx.commit()
        
        # 插入填料信息（200条）
        insert_fillers(cursor, count=200)
        cnx.commit()
        
        # 插入配方成分（3000条，平均每个项目3个成分）
        insert_formula_compositions(cursor, count=3000)
        cnx.commit()
        
        # 插入测试结果
        insert_test_results(cursor)
        cnx.commit()
        
        # 统计数据
        logger.info("\n" + "=" * 60)
        logger.info("数据插入完成！数据统计：")
        logger.info("=" * 60)
        
        tables = [
            ('tbl_ProjectInfo', '项目信息'),
            ('tbl_RawMaterials', '原料信息'),
            ('tbl_InorganicFillers', '填料信息'),
            ('tbl_FormulaComposition', '配方成分'),
            ('tbl_TestResults_Ink', '喷墨测试'),
            ('tbl_TestResults_Coating', '涂层测试'),
            ('tbl_TestResults_3DPrint', '3D打印测试'),
            ('tbl_TestResults_Composite', '复合材料测试')
        ]
        
        for table_name, display_name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            logger.info(f"{display_name:20s}: {count:6d} 条")
        
        logger.info("=" * 60)
        logger.info("✓ 所有测试数据插入成功！")
        
    except mysql.connector.Error as err:
        logger.error(f"✗ 发生数据库错误: {err}")
        if 'cnx' in locals():
            cnx.rollback()
    except Exception as e:
        logger.error(f"✗ 发生错误: {e}")
        if 'cnx' in locals():
            cnx.rollback()
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()
            logger.info("MySQL 连接已关闭。")

if __name__ == "__main__":
    main()

