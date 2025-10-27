import mysql.connector
from mysql.connector import errorcode
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DB_NAME = config.DB_CONFIG['database']


TABLES = {}
# 项目类型配置表
TABLES['tbl_Config_ProjectTypes'] = (
    "CREATE TABLE `tbl_Config_ProjectTypes` ("
    "  `TypeID` int(11) NOT NULL AUTO_INCREMENT COMMENT '类型ID',"
    "  `TypeName` varchar(255) NOT NULL COMMENT '类型名称',"
    "  `TypeCode` varchar(10) NOT NULL COMMENT '类型代码',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`TypeID`)"
    ") ENGINE=InnoDB COMMENT='项目类型配置表'")
# 材料类别配置表
TABLES['tbl_Config_MaterialCategories'] = (
    "CREATE TABLE `tbl_Config_MaterialCategories` ("
    "  `CategoryID` int(11) NOT NULL AUTO_INCREMENT COMMENT '类别ID',"
    "  `CategoryName` varchar(255) NOT NULL COMMENT '类别名称',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`CategoryID`)"
    ") ENGINE=InnoDB COMMENT='原料类别配置表'")

TABLES['tbl_Config_FillerTypes'] = (
    "CREATE TABLE `tbl_Config_FillerTypes` ("
    "  `FillerTypeID` int(11) NOT NULL AUTO_INCREMENT COMMENT '填料类型ID',"
    "  `FillerTypeName` varchar(255) NOT NULL COMMENT '填料类型名称',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`FillerTypeID`)"
    ") ENGINE=InnoDB COMMENT='无机填料类型配置表'")

# 项目信息表
TABLES['tbl_ProjectInfo'] = (
    "CREATE TABLE `tbl_ProjectInfo` ("
    "  `ProjectID` int(11) NOT NULL AUTO_INCREMENT COMMENT '项目ID',"
    "  `ProjectName` varchar(255) NOT NULL COMMENT '项目名称',"
    "  `ProjectType_FK` int(11) COMMENT '项目类型外键',"
    "  `SubstrateApplication` text COMMENT '目标基材或应用领域',"
    "  `FormulatorName` varchar(255) COMMENT '配方设计师姓名',"
    "  `FormulationDate` date COMMENT '配方设计日期',"
    "  `FormulaCode` varchar(255) UNIQUE COMMENT '配方编码',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`ProjectID`),"
    "  FOREIGN KEY (`ProjectType_FK`) REFERENCES `tbl_Config_ProjectTypes` (`TypeID`) ON DELETE SET NULL"
    ") ENGINE=InnoDB COMMENT='项目基本信息表'")
# 原料表
TABLES['tbl_RawMaterials'] = (
    "CREATE TABLE `tbl_RawMaterials` ("
    "  `MaterialID` int(11) NOT NULL AUTO_INCREMENT COMMENT '原料ID',"
    "  `TradeName` varchar(255) NOT NULL COMMENT '商品名称',"
    "  `Category_FK` int(11) COMMENT '类别外键',"
    "  `Supplier` varchar(255) COMMENT '供应商',"
    "  `CAS_Number` varchar(255) COMMENT '化学文摘登记号',"
    "  `Density` decimal(10,4) COMMENT '密度',"
    "  `Viscosity` decimal(10,4) COMMENT '粘度',"
    "  `FunctionDescription` text COMMENT '功能说明',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`MaterialID`),"
    "  FOREIGN KEY (`Category_FK`) REFERENCES `tbl_Config_MaterialCategories` (`CategoryID`) ON DELETE SET NULL"
    ") ENGINE=InnoDB COMMENT='原料信息主表'")
# 无机材料表
TABLES['tbl_InorganicFillers'] = (
    "CREATE TABLE `tbl_InorganicFillers` ("
    "  `FillerID` int(11) NOT NULL AUTO_INCREMENT COMMENT '填料ID',"
    "  `TradeName` varchar(255) NOT NULL COMMENT '商品名称',"
    "  `FillerType_FK` int(11) COMMENT '填料类型外键',"
    "  `Supplier` varchar(255) COMMENT '供应商',"
    "  `ParticleSize` varchar(255) COMMENT '粒径（含D50）',"
    "  `IsSilanized` tinyint(1) DEFAULT 0 COMMENT '是否硅烷化 (1:是, 0:否)',"
    "  `CouplingAgent` varchar(255) COMMENT '所用偶联剂',"
    "  `SurfaceArea` decimal(10,4) COMMENT '比表面积 (m²/g)',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`FillerID`),"
    "  FOREIGN KEY (`FillerType_FK`) REFERENCES `tbl_Config_FillerTypes` (`FillerTypeID`) ON DELETE SET NULL"
    ") ENGINE=InnoDB COMMENT='无机填料信息主表'")
# 化学成分表
TABLES['tbl_FormulaComposition'] = (
    "CREATE TABLE `tbl_FormulaComposition` ("
    "  `CompositionID` int(11) NOT NULL AUTO_INCREMENT COMMENT '成分ID',"
    "  `ProjectID_FK` int(11) NOT NULL COMMENT '项目ID外键',"
    "  `MaterialID_FK` int(11) COMMENT '原料ID外键',"
    "  `FillerID_FK` int(11) COMMENT '填料ID外键',"
    "  `WeightPercentage` decimal(7,4) NOT NULL COMMENT '重量百分比(%)',"
    "  `AdditionMethod` text COMMENT '掺入方法',"
    "  `Remarks` text COMMENT '备注',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`CompositionID`),"
    "  FOREIGN KEY (`ProjectID_FK`) REFERENCES `tbl_ProjectInfo` (`ProjectID`) ON DELETE CASCADE,"
    "  FOREIGN KEY (`MaterialID_FK`) REFERENCES `tbl_RawMaterials` (`MaterialID`) ON DELETE SET NULL,"
    "  FOREIGN KEY (`FillerID_FK`) REFERENCES `tbl_InorganicFillers` (`FillerID`) ON DELETE SET NULL"
    ") ENGINE=InnoDB COMMENT='配方成分表'")
# 测试结果表 - 喷墨
TABLES['tbl_TestResults_Ink'] = (
    "CREATE TABLE `tbl_TestResults_Ink` ("
    "  `ResultID` int(11) NOT NULL AUTO_INCREMENT COMMENT '结果ID',"
    "  `ProjectID_FK` int(11) NOT NULL COMMENT '项目ID外键',"
    "  `Ink_Viscosity` varchar(255) COMMENT '粘度',"
    "  `Ink_Reactivity` varchar(255) COMMENT '反应活性/固化时间',"
    "  `Ink_ParticleSize` varchar(255) COMMENT '粒径(nm)',"
    "  `Ink_SurfaceTension` varchar(255) COMMENT '表面张力(mN/m)',"
    "  `Ink_ColorValue` varchar(255) COMMENT '色度(Lab*色值)',"
    "  `Ink_RheologyNote` text COMMENT '流变学说明或文件',"
    "  `TestDate` date COMMENT '测试日期',"
    "  `Notes` text COMMENT '备注',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`ResultID`),"
    "  UNIQUE KEY (`ProjectID_FK`),"
    "  FOREIGN KEY (`ProjectID_FK`) REFERENCES `tbl_ProjectInfo` (`ProjectID`) ON DELETE CASCADE"
    ") ENGINE=InnoDB COMMENT='测试结果数据表-喷墨'")

# 测试结果表 - 涂层
TABLES['tbl_TestResults_Coating'] = (
    "CREATE TABLE `tbl_TestResults_Coating` ("
    "  `ResultID` int(11) NOT NULL AUTO_INCREMENT COMMENT '结果ID',"
    "  `ProjectID_FK` int(11) NOT NULL COMMENT '项目ID外键',"
    "  `Coating_Adhesion` varchar(255) COMMENT '附着力',"
    "  `Coating_Transparency` varchar(255) COMMENT '透明度',"
    "  `Coating_SurfaceHardness` varchar(255) COMMENT '表面硬度',"
    "  `Coating_ChemicalResistance` varchar(255) COMMENT '耐化学性',"
    "  `Coating_CostEstimate` varchar(255) COMMENT '成本估算(€/kg)',"
    "  `TestDate` date COMMENT '测试日期',"
    "  `Notes` text COMMENT '备注',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`ResultID`),"
    "  UNIQUE KEY (`ProjectID_FK`),"
    "  FOREIGN KEY (`ProjectID_FK`) REFERENCES `tbl_ProjectInfo` (`ProjectID`) ON DELETE CASCADE"
    ") ENGINE=InnoDB COMMENT='测试结果数据表-涂层'")

# 测试结果表 - 3D打印
TABLES['tbl_TestResults_3DPrint'] = (
    "CREATE TABLE `tbl_TestResults_3DPrint` ("
    "  `ResultID` int(11) NOT NULL AUTO_INCREMENT COMMENT '结果ID',"
    "  `ProjectID_FK` int(11) NOT NULL COMMENT '项目ID外键',"
    "  `Print3D_Shrinkage` varchar(255) COMMENT '收缩率(%)',"
    "  `Print3D_YoungsModulus` varchar(255) COMMENT '杨氏模量',"
    "  `Print3D_FlexuralStrength` varchar(255) COMMENT '弯曲强度',"
    "  `Print3D_ShoreHardness` varchar(255) COMMENT '邵氏硬度',"
    "  `Print3D_ImpactResistance` varchar(255) COMMENT '抗冲击性',"
    "  `TestDate` date COMMENT '测试日期',"
    "  `Notes` text COMMENT '备注',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`ResultID`),"
    "  UNIQUE KEY (`ProjectID_FK`),"
    "  FOREIGN KEY (`ProjectID_FK`) REFERENCES `tbl_ProjectInfo` (`ProjectID`) ON DELETE CASCADE"
    ") ENGINE=InnoDB COMMENT='测试结果数据表-3D打印'")

# 用户账号表
TABLES['tbl_Users'] = (
    "CREATE TABLE `tbl_Users` ("
    "  `UserID` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID',"
    "  `Username` varchar(50) NOT NULL UNIQUE COMMENT '用户名',"
    "  `PasswordHash` varchar(255) NOT NULL COMMENT '密码哈希（Argon2id）',"
    "  `RealName` varchar(100) COMMENT '真实姓名',"
    "  `Position` varchar(100) COMMENT '职位',"
    "  `Role` enum('admin', 'user') NOT NULL DEFAULT 'user' COMMENT '角色：admin-管理员，user-普通用户',"
    "  `Email` varchar(255) COMMENT '邮箱',"
    "  `IsActive` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否激活（1:是，0:否）',"
    "  `CreatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',"
    "  `LastLogin` datetime COMMENT '最后登录时间',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`UserID`),"
    "  UNIQUE KEY (`Username`)"
    ") ENGINE=InnoDB COMMENT='用户账号管理表'")

# 系统信息表
TABLES['tbl_SystemInfo'] = (
    "CREATE TABLE `tbl_SystemInfo` ("
    "  `InfoID` int(11) NOT NULL AUTO_INCREMENT COMMENT '信息ID',"
    "  `FirstStartTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '系统首次启动时间',"
    "  `Version` varchar(50) COMMENT '系统版本',"
    "  `LastUpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',"
    "  PRIMARY KEY (`InfoID`)"
    ") ENGINE=InnoDB COMMENT='系统信息表'")

# 用户登录日志表
TABLES['tbl_UserLoginLogs'] = (
    "CREATE TABLE `tbl_UserLoginLogs` ("
    "  `LogID` int(11) NOT NULL AUTO_INCREMENT COMMENT '日志ID',"
    "  `UserID` int(11) NOT NULL COMMENT '用户ID',"
    "  `Username` varchar(50) NOT NULL COMMENT '用户名',"
    "  `LoginTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',"
    "  `LogoutTime` datetime COMMENT '登出时间',"
    "  `Duration` int(11) COMMENT '使用时长（秒）',"
    "  `IPAddress` varchar(50) COMMENT '登录IP地址',"
    "  `UserAgent` text COMMENT '用户代理信息',"
    "  `IsOnline` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否在线（1:是，0:否）',"
    "  `LastHeartbeat` datetime COMMENT '最后心跳时间',"
    "  PRIMARY KEY (`LogID`),"
    "  INDEX `idx_login_user_id` (`UserID`),"
    "  INDEX `idx_login_username` (`Username`),"
    "  INDEX `idx_login_time` (`LoginTime`),"
    "  INDEX `idx_login_is_online` (`IsOnline`),"
    "  FOREIGN KEY (`UserID`) REFERENCES `tbl_Users` (`UserID`) ON DELETE CASCADE"
    ") ENGINE=InnoDB COMMENT='用户登录日志表'")

# 用户注册日志表
TABLES['tbl_UserRegistrationLogs'] = (
    "CREATE TABLE `tbl_UserRegistrationLogs` ("
    "  `LogID` int(11) NOT NULL AUTO_INCREMENT COMMENT '日志ID',"
    "  `UserID` int(11) NOT NULL COMMENT '用户ID',"
    "  `Username` varchar(50) NOT NULL COMMENT '用户名',"
    "  `RegistrationTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',"
    "  `RealName` varchar(50) COMMENT '真实姓名',"
    "  `Position` varchar(100) COMMENT '职位',"
    "  `Email` varchar(100) COMMENT '邮箱',"
    "  `Role` varchar(20) NOT NULL DEFAULT 'user' COMMENT '角色',"
    "  `IPAddress` varchar(50) COMMENT '注册IP地址',"
    "  PRIMARY KEY (`LogID`),"
    "  INDEX `idx_reg_user_id` (`UserID`),"
    "  INDEX `idx_reg_username` (`Username`),"
    "  INDEX `idx_reg_time` (`RegistrationTime`),"
    "  FOREIGN KEY (`UserID`) REFERENCES `tbl_Users` (`UserID`) ON DELETE CASCADE"
    ") ENGINE=InnoDB COMMENT='用户注册日志表'")

# 测试结果表 - 复合材料
TABLES['tbl_TestResults_Composite'] = (
    "CREATE TABLE `tbl_TestResults_Composite` ("
    "  `ResultID` int(11) NOT NULL AUTO_INCREMENT COMMENT '结果ID',"
    "  `ProjectID_FK` int(11) NOT NULL COMMENT '项目ID外键',"
    "  `Composite_FlexuralStrength` varchar(255) COMMENT '弯曲强度',"
    "  `Composite_YoungsModulus` varchar(255) COMMENT '杨氏模量',"
    "  `Composite_ImpactResistance` varchar(255) COMMENT '抗冲击性',"
    "  `Composite_ConversionRate` varchar(255) COMMENT '转化率(可选)',"
    "  `Composite_WaterAbsorption` varchar(255) COMMENT '吸水率/溶解度(可选)',"
    "  `TestDate` date COMMENT '测试日期',"
    "  `Notes` text COMMENT '备注',"
    "  `ReservedField1` text COMMENT '备用字段1',"
    "  `ReservedField2` text COMMENT '备用字段2',"
    "  PRIMARY KEY (`ResultID`),"
    "  UNIQUE KEY (`ProjectID_FK`),"
    "  FOREIGN KEY (`ProjectID_FK`) REFERENCES `tbl_ProjectInfo` (`ProjectID`) ON DELETE CASCADE"
    ") ENGINE=InnoDB COMMENT='测试结果数据表-复合材料'")

# ============================================
# 索引定义
# ============================================
INDEXES = {
    # 用户表索引
    'tbl_Users': [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON tbl_Users(Email)",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON tbl_Users(Role)",
        "CREATE INDEX IF NOT EXISTS idx_users_is_active ON tbl_Users(IsActive)",
        "CREATE INDEX IF NOT EXISTS idx_users_last_login ON tbl_Users(LastLogin)",
        "CREATE INDEX IF NOT EXISTS idx_users_role_active ON tbl_Users(Role, IsActive)"
    ],
    
    # 项目信息表索引
    'tbl_ProjectInfo': [
        "CREATE INDEX IF NOT EXISTS idx_project_type_fk ON tbl_ProjectInfo(ProjectType_FK)",
        "CREATE INDEX IF NOT EXISTS idx_project_formulation_date ON tbl_ProjectInfo(FormulationDate)",
        "CREATE INDEX IF NOT EXISTS idx_project_formulator ON tbl_ProjectInfo(FormulatorName)",
        "CREATE INDEX IF NOT EXISTS idx_project_type_date ON tbl_ProjectInfo(ProjectType_FK, FormulationDate)"
    ],
    
    # 原料表索引
    'tbl_RawMaterials': [
        "CREATE INDEX IF NOT EXISTS idx_material_category_fk ON tbl_RawMaterials(Category_FK)",
        "CREATE INDEX IF NOT EXISTS idx_material_supplier ON tbl_RawMaterials(Supplier)",
        "CREATE INDEX IF NOT EXISTS idx_material_cas ON tbl_RawMaterials(CAS_Number)",
        "CREATE INDEX IF NOT EXISTS idx_material_trade_name ON tbl_RawMaterials(TradeName)"
    ],
    
    # 无机填料表索引
    'tbl_InorganicFillers': [
        "CREATE INDEX IF NOT EXISTS idx_filler_type_fk ON tbl_InorganicFillers(FillerType_FK)",
        "CREATE INDEX IF NOT EXISTS idx_filler_supplier ON tbl_InorganicFillers(Supplier)",
        "CREATE INDEX IF NOT EXISTS idx_filler_trade_name ON tbl_InorganicFillers(TradeName)",
        "CREATE INDEX IF NOT EXISTS idx_filler_silanized ON tbl_InorganicFillers(IsSilanized)"
    ],
    
    # 配方成分表索引（非常重要！）
    'tbl_FormulaComposition': [
        "CREATE INDEX IF NOT EXISTS idx_composition_project_fk ON tbl_FormulaComposition(ProjectID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_composition_material_fk ON tbl_FormulaComposition(MaterialID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_composition_filler_fk ON tbl_FormulaComposition(FillerID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_composition_project_material ON tbl_FormulaComposition(ProjectID_FK, MaterialID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_composition_project_filler ON tbl_FormulaComposition(ProjectID_FK, FillerID_FK)"
    ],
    
    # 测试结果表索引
    'tbl_TestResults_Ink': [
        "CREATE INDEX IF NOT EXISTS idx_test_ink_project_fk ON tbl_TestResults_Ink(ProjectID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_test_ink_date ON tbl_TestResults_Ink(TestDate)"
    ],
    
    'tbl_TestResults_Coating': [
        "CREATE INDEX IF NOT EXISTS idx_test_coating_project_fk ON tbl_TestResults_Coating(ProjectID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_test_coating_date ON tbl_TestResults_Coating(TestDate)"
    ],
    
    'tbl_TestResults_3DPrint': [
        "CREATE INDEX IF NOT EXISTS idx_test_3d_project_fk ON tbl_TestResults_3DPrint(ProjectID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_test_3d_date ON tbl_TestResults_3DPrint(TestDate)"
    ],
    
    'tbl_TestResults_Composite': [
        "CREATE INDEX IF NOT EXISTS idx_test_composite_project_fk ON tbl_TestResults_Composite(ProjectID_FK)",
        "CREATE INDEX IF NOT EXISTS idx_test_composite_date ON tbl_TestResults_Composite(TestDate)"
    ],
    
    # 登录日志表索引
    'tbl_UserLoginLogs': [
        "CREATE INDEX IF NOT EXISTS idx_login_user_time ON tbl_UserLoginLogs(UserID, LoginTime)",
        "CREATE INDEX IF NOT EXISTS idx_login_duration ON tbl_UserLoginLogs(Duration)",
        "CREATE INDEX IF NOT EXISTS idx_login_heartbeat ON tbl_UserLoginLogs(LastHeartbeat)",
        "CREATE INDEX IF NOT EXISTS idx_login_online_heartbeat ON tbl_UserLoginLogs(IsOnline, LastHeartbeat)"
    ],
    
    # 注册日志表索引
    'tbl_UserRegistrationLogs': [
        "CREATE INDEX IF NOT EXISTS idx_reg_user_time ON tbl_UserRegistrationLogs(UserID, RegistrationTime)",
        "CREATE INDEX IF NOT EXISTS idx_reg_role ON tbl_UserRegistrationLogs(Role)"
    ]
}

def create_database(cursor):
    """创建数据库，使用 utf8mb4 字符集"""
    try:
        cursor.execute(
            f"CREATE DATABASE {DB_NAME} "
            "DEFAULT CHARACTER SET 'utf8mb4' "
            "DEFAULT COLLATE 'utf8mb4_unicode_ci'"
        )
        logger.info(f"数据库 {DB_NAME} 创建完毕。")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            logger.info(f"数据库 {DB_NAME} 已存在。")
        else:
            logger.error(f"创建数据库失败: {err}")
            exit(1)

def create_indexes(cursor):
    """创建性能优化索引"""
    logger.info("\n开始创建性能优化索引...")
    index_count = 0
    skipped_count = 0
    
    for table_name, index_list in INDEXES.items():
        logger.info(f"\n为表 `{table_name}` 创建索引...")
        for index_sql in index_list:
            try:
                cursor.execute(index_sql)
                # 提取索引名称用于日志
                index_name = index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unknown'
                logger.info(f"  ✓ 索引 idx_{index_name} 创建成功")
                index_count += 1
            except mysql.connector.Error as err:
                if err.errno == 1061:  # ER_DUP_KEYNAME
                    index_name = index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unknown'
                    logger.info(f"  - 索引 idx_{index_name} 已存在，跳过")
                    skipped_count += 1
                else:
                    logger.error(f"  ✗ 索引创建失败: {err}")
    
    logger.info(f"\n索引创建完成！共创建 {index_count} 个索引，跳过 {skipped_count} 个已存在的索引。")

def main():
    """主函数：创建数据库和所有表"""
    # Establish connection to MySQL server
    try:
        # 先连接到服务器（不指定数据库）
        base_config = {k: v for k, v in config.DB_CONFIG.items() if k != 'database'}
        cnx = mysql.connector.connect(**base_config)
        cursor = cnx.cursor()
        logger.info("成功连接到 MySQL 服务器。")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logger.error("数据库用户名或密码错误。")
        else:
            logger.error(f"连接失败: {err}")
        return

    # Create database if it doesn't exist, and select it
    create_database(cursor)
    try:
        cnx.database = DB_NAME
        logger.info(f"已切换到数据库: {DB_NAME}")
    except mysql.connector.Error as err:
        logger.error(f"切换数据库失败 {DB_NAME}: {err}")
        cnx.close()
        return

    # Create tables
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            logger.info(f"正在创建表 `{table_name}`...")
            cursor.execute(table_description)
            logger.info(f"✓ 表 `{table_name}` 创建成功")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                logger.info(f"- 表 `{table_name}` 已存在，跳过")
            else:
                logger.error(f"✗ 表 `{table_name}` 创建失败: {err.msg}")
    
    logger.info("\n所有表已处理完成。")
    
    # 创建性能优化索引
    create_indexes(cursor)
    
    logger.info("\n数据库设置完成！")
    cursor.close()
    cnx.close()
    logger.info("MySQL 连接已关闭。")

if __name__ == "__main__":
    main()
