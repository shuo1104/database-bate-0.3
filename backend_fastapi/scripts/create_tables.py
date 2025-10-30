import psycopg2
from psycopg2 import errors
import os
from pathlib import Path

# 尝试加载 .env 文件
def load_env_file():
    env_file = Path(__file__).parent / 'backend_fastapi' / 'env' / '.env.dev'
    if env_file.exists():
        for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']:
            try:
                with open(env_file, 'r', encoding=encoding) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() not in os.environ:
                                os.environ[key.strip()] = value.strip()
                print("Configuration file loaded successfully")
                return
            except UnicodeDecodeError:
                continue

load_env_file()

# 数据库连接配置
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME = os.getenv('DB_DATABASE', 'photopolymer_formulation_db')

# 表定义
TABLES = {}

TABLES['tbl_Config_ProjectTypes'] = (
    'CREATE TABLE "tbl_Config_ProjectTypes" ('
    '  "TypeID" SERIAL PRIMARY KEY,'
    '  "TypeName" VARCHAR(255) NOT NULL,'
    '  "TypeCode" VARCHAR(10) NOT NULL,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT'
    '); '
)

TABLES['tbl_Config_MaterialCategories'] = (
    'CREATE TABLE "tbl_Config_MaterialCategories" ('
    '  "CategoryID" SERIAL PRIMARY KEY,'
    '  "CategoryName" VARCHAR(255) NOT NULL,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT'
    '); '
)

TABLES['tbl_Config_FillerTypes'] = (
    'CREATE TABLE "tbl_Config_FillerTypes" ('
    '  "FillerTypeID" SERIAL PRIMARY KEY,'
    '  "FillerTypeName" VARCHAR(255) NOT NULL,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT'
    '); '
)

TABLES['tbl_ProjectInfo'] = (
    'CREATE TABLE "tbl_ProjectInfo" ('
    '  "ProjectID" SERIAL PRIMARY KEY,'
    '  "ProjectName" VARCHAR(255) NOT NULL,'
    '  "ProjectType_FK" INTEGER,'
    '  "SubstrateApplication" TEXT,'
    '  "FormulatorName" VARCHAR(255),'
    '  "FormulationDate" DATE,'
    '  "FormulaCode" VARCHAR(255) UNIQUE,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT,'
    '  FOREIGN KEY ("ProjectType_FK") REFERENCES "tbl_Config_ProjectTypes" ("TypeID") ON DELETE SET NULL'
    '); '
    'CREATE INDEX IF NOT EXISTS idx_project_type_fk ON "tbl_ProjectInfo"("ProjectType_FK"); '
)

TABLES['tbl_RawMaterials'] = (
    'CREATE TABLE "tbl_RawMaterials" ('
    '  "MaterialID" SERIAL PRIMARY KEY,'
    '  "TradeName" VARCHAR(255) NOT NULL,'
    '  "Category_FK" INTEGER,'
    '  "Supplier" VARCHAR(255),'
    '  "CAS_Number" VARCHAR(255),'
    '  "Density" DECIMAL(10,4),'
    '  "Viscosity" DECIMAL(10,4),'
    '  "FunctionDescription" TEXT,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT,'
    '  FOREIGN KEY ("Category_FK") REFERENCES "tbl_Config_MaterialCategories" ("CategoryID") ON DELETE SET NULL'
    '); '
    'CREATE INDEX IF NOT EXISTS idx_material_category_fk ON "tbl_RawMaterials"("Category_FK"); '
)

TABLES['tbl_InorganicFillers'] = (
    'CREATE TABLE "tbl_InorganicFillers" ('
    '  "FillerID" SERIAL PRIMARY KEY,'
    '  "TradeName" VARCHAR(255) NOT NULL,'
    '  "FillerType_FK" INTEGER,'
    '  "Supplier" VARCHAR(255),'
    '  "ParticleSize" VARCHAR(255),'
    '  "IsSilanized" SMALLINT DEFAULT 0,'
    '  "CouplingAgent" VARCHAR(255),'
    '  "SurfaceArea" DECIMAL(10,4),'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT,'
    '  FOREIGN KEY ("FillerType_FK") REFERENCES "tbl_Config_FillerTypes" ("FillerTypeID") ON DELETE SET NULL'
    '); '
    'CREATE INDEX IF NOT EXISTS idx_filler_type_fk ON "tbl_InorganicFillers"("FillerType_FK"); '
)

TABLES['tbl_FormulaComposition'] = (
    'CREATE TABLE "tbl_FormulaComposition" ('
    '  "CompositionID" SERIAL PRIMARY KEY,'
    '  "ProjectID_FK" INTEGER NOT NULL,'
    '  "MaterialID_FK" INTEGER,'
    '  "FillerID_FK" INTEGER,'
    '  "WeightPercentage" DECIMAL(7,4) NOT NULL,'
    '  "AdditionMethod" TEXT,'
    '  "Remarks" TEXT,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT,'
    '  FOREIGN KEY ("ProjectID_FK") REFERENCES "tbl_ProjectInfo" ("ProjectID") ON DELETE CASCADE,'
    '  FOREIGN KEY ("MaterialID_FK") REFERENCES "tbl_RawMaterials" ("MaterialID") ON DELETE SET NULL,'
    '  FOREIGN KEY ("FillerID_FK") REFERENCES "tbl_InorganicFillers" ("FillerID") ON DELETE SET NULL'
    '); '
    'CREATE INDEX IF NOT EXISTS idx_composition_project_fk ON "tbl_FormulaComposition"("ProjectID_FK"); '
)

TABLES['tbl_TestResults_Ink'] = (
    'CREATE TABLE "tbl_TestResults_Ink" ('
    '  "ResultID" SERIAL PRIMARY KEY,'
    '  "ProjectID_FK" INTEGER NOT NULL UNIQUE,'
    '  "Ink_Viscosity" VARCHAR(255),'
    '  "Ink_Reactivity" VARCHAR(255),'
    '  "Ink_ParticleSize" VARCHAR(255),'
    '  "Ink_SurfaceTension" VARCHAR(255),'
    '  "Ink_ColorValue" VARCHAR(255),'
    '  "Ink_RheologyNote" TEXT,'
    '  "TestDate" DATE,'
    '  "Notes" TEXT,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT,'
    '  FOREIGN KEY ("ProjectID_FK") REFERENCES "tbl_ProjectInfo" ("ProjectID") ON DELETE CASCADE'
    '); '
)

TABLES['tbl_TestResults_Coating'] = (
    'CREATE TABLE "tbl_TestResults_Coating" ('
    '  "ResultID" SERIAL PRIMARY KEY,'
    '  "ProjectID_FK" INTEGER NOT NULL UNIQUE,'
    '  "Coating_Adhesion" VARCHAR(255),'
    '  "Coating_Transparency" VARCHAR(255),'
    '  "Coating_SurfaceHardness" VARCHAR(255),'
    '  "Coating_ChemicalResistance" VARCHAR(255),'
    '  "Coating_CostEstimate" VARCHAR(255),'
    '  "TestDate" DATE,'
    '  "Notes" TEXT,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT,'
    '  FOREIGN KEY ("ProjectID_FK") REFERENCES "tbl_ProjectInfo" ("ProjectID") ON DELETE CASCADE'
    '); '
)

TABLES['tbl_TestResults_3DPrint'] = (
    'CREATE TABLE "tbl_TestResults_3DPrint" ('
    '  "ResultID" SERIAL PRIMARY KEY,'
    '  "ProjectID_FK" INTEGER NOT NULL UNIQUE,'
    '  "Print3D_Shrinkage" VARCHAR(255),'
    '  "Print3D_YoungsModulus" VARCHAR(255),'
    '  "Print3D_FlexuralStrength" VARCHAR(255),'
    '  "Print3D_ShoreHardness" VARCHAR(255),'
    '  "Print3D_ImpactResistance" VARCHAR(255),'
    '  "TestDate" DATE,'
    '  "Notes" TEXT,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT,'
    '  FOREIGN KEY ("ProjectID_FK") REFERENCES "tbl_ProjectInfo" ("ProjectID") ON DELETE CASCADE'
    '); '
)

TABLES['tbl_TestResults_Composite'] = (
    'CREATE TABLE "tbl_TestResults_Composite" ('
    '  "ResultID" SERIAL PRIMARY KEY,'
    '  "ProjectID_FK" INTEGER NOT NULL UNIQUE,'
    '  "Composite_FlexuralStrength" VARCHAR(255),'
    '  "Composite_YoungsModulus" VARCHAR(255),'
    '  "Composite_ImpactResistance" VARCHAR(255),'
    '  "Composite_ConversionRate" VARCHAR(255),'
    '  "Composite_WaterAbsorption" VARCHAR(255),'
    '  "TestDate" DATE,'
    '  "Notes" TEXT,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT,'
    '  FOREIGN KEY ("ProjectID_FK") REFERENCES "tbl_ProjectInfo" ("ProjectID") ON DELETE CASCADE'
    '); '
)

TABLES['tbl_Users'] = (
    'CREATE TABLE "tbl_Users" ('
    '  "UserID" SERIAL PRIMARY KEY,'
    '  "Username" VARCHAR(50) NOT NULL UNIQUE,'
    '  "PasswordHash" VARCHAR(255) NOT NULL,'
    '  "RealName" VARCHAR(100),'
    '  "Position" VARCHAR(100),'
    '  "Role" VARCHAR(20) NOT NULL DEFAULT \'user\' CHECK ("Role" IN (\'admin\', \'user\')),'
    '  "Email" VARCHAR(255),'
    '  "IsActive" SMALLINT NOT NULL DEFAULT 1,'
    '  "CreatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,'
    '  "LastLogin" TIMESTAMP,'
    '  "ReservedField1" TEXT,'
    '  "ReservedField2" TEXT'
    '); '
    'CREATE INDEX IF NOT EXISTS idx_users_email ON "tbl_Users"("Email"); '
)

TABLES['tbl_SystemInfo'] = (
    'CREATE TABLE "tbl_SystemInfo" ('
    '  "InfoID" SERIAL PRIMARY KEY,'
    '  "FirstStartTime" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,'
    '  "Version" VARCHAR(50),'
    '  "LastUpdateTime" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP'
    '); '
)

TABLES['tbl_UserLoginLogs'] = (
    'CREATE TABLE "tbl_UserLoginLogs" ('
    '  "LogID" SERIAL PRIMARY KEY,'
    '  "UserID" INTEGER NOT NULL,'
    '  "Username" VARCHAR(50) NOT NULL,'
    '  "LoginTime" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,'
    '  "LogoutTime" TIMESTAMP,'
    '  "Duration" INTEGER,'
    '  "IPAddress" VARCHAR(50),'
    '  "UserAgent" TEXT,'
    '  "IsOnline" SMALLINT NOT NULL DEFAULT 1,'
    '  "LastHeartbeat" TIMESTAMP,'
    '  FOREIGN KEY ("UserID") REFERENCES "tbl_Users" ("UserID") ON DELETE CASCADE'
    '); '
    'CREATE INDEX IF NOT EXISTS idx_login_user_id ON "tbl_UserLoginLogs"("UserID"); '
)

TABLES['tbl_UserRegistrationLogs'] = (
    'CREATE TABLE "tbl_UserRegistrationLogs" ('
    '  "LogID" SERIAL PRIMARY KEY,'
    '  "UserID" INTEGER NOT NULL,'
    '  "Username" VARCHAR(50) NOT NULL,'
    '  "RegistrationTime" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,'
    '  "RealName" VARCHAR(50),'
    '  "Position" VARCHAR(100),'
    '  "Email" VARCHAR(100),'
    '  "Role" VARCHAR(20) NOT NULL DEFAULT \'user\','
    '  "IPAddress" VARCHAR(50),'
    '  FOREIGN KEY ("UserID") REFERENCES "tbl_Users" ("UserID") ON DELETE CASCADE'
    '); '
    'CREATE INDEX IF NOT EXISTS idx_reg_user_id ON "tbl_UserRegistrationLogs"("UserID"); '
)

# 表创建顺序
TABLE_ORDER = [
    'tbl_Config_ProjectTypes',
    'tbl_Config_MaterialCategories',
    'tbl_Config_FillerTypes',
    'tbl_Users',
    'tbl_ProjectInfo',
    'tbl_RawMaterials',
    'tbl_InorganicFillers',
    'tbl_FormulaComposition',
    'tbl_TestResults_Ink',
    'tbl_TestResults_Coating',
    'tbl_TestResults_3DPrint',
    'tbl_TestResults_Composite',
    'tbl_SystemInfo',
    'tbl_UserLoginLogs',
    'tbl_UserRegistrationLogs',
]

# 基础数据
PROJECT_TYPES = [
    ("Inkjet", "INK"),
    ("Coating", "COAT"),
    ("3D Printing", "3DP"),
    ("Composite", "COMP"),
]

MATERIAL_CATEGORIES = [
    "Monomer",
    "Oligomer",
    "Photoinitiator",
    "Additive",
    "Pigment",
    "Solvent",
]

FILLER_TYPES = [
    "Glass",
    "Silica",
    "ZrO2",
]


def main():
    print("=" * 60)
    print("PostgreSQL Database Initialization")
    print("=" * 60)
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"Database: {DB_NAME}")
    print("=" * 60)
    
    # Connect to PostgreSQL server
    try:
        cnx = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        cnx.autocommit = True
        cursor = cnx.cursor()
        print("+ Connected to PostgreSQL server")
    except Exception as err:
        print(f"X Connection failed: {err}")
        return
    
    # Create database
    try:
        cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"+ Database '{DB_NAME}' created")
    except errors.DuplicateDatabase:
        print(f"- Database '{DB_NAME}' already exists")
    except Exception as err:
        print(f"X Failed to create database: {err}")
        return
    
    cursor.close()
    cnx.close()
    
    # Connect to target database
    try:
        cnx = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cnx.autocommit = False
        cursor = cnx.cursor()
        print(f"+ Connected to database '{DB_NAME}'")
    except Exception as err:
        print(f"X Failed to connect to database: {err}")
        return
    
    # Create tables
    print("\n" + "=" * 60)
    print("Creating tables...")
    print("=" * 60)
    created = 0
    skipped = 0
    
    for table_name in TABLE_ORDER:
        try:
            cursor.execute(TABLES[table_name])
            cnx.commit()
            print(f"+ Table '{table_name}' created")
            created += 1
        except errors.DuplicateTable:
            cnx.rollback()
            skipped += 1
        except Exception as err:
            print(f"X Failed to create '{table_name}': {err}")
            cnx.rollback()
    
    print(f"\nSummary: {created} created, {skipped} skipped")
    
    # Initialize project types
    print("\n" + "=" * 60)
    print("Initializing data...")
    print("=" * 60)
    
    try:
        cursor.execute('SELECT COUNT(*) FROM "tbl_Config_ProjectTypes"')
        if cursor.fetchone()[0] == 0:
            for type_name, type_code in PROJECT_TYPES:
                cursor.execute(
                    'INSERT INTO "tbl_Config_ProjectTypes" ("TypeName", "TypeCode") VALUES (%s, %s)',
                    (type_name, type_code)
                )
            cnx.commit()
            print(f"+ Initialized {len(PROJECT_TYPES)} project types")
        else:
            print("- Project types already exist")
    except Exception as err:
        print(f"X Failed to initialize project types: {err}")
        cnx.rollback()
    
    # Initialize material categories
    try:
        cursor.execute('SELECT COUNT(*) FROM "tbl_Config_MaterialCategories"')
        if cursor.fetchone()[0] == 0:
            for category in MATERIAL_CATEGORIES:
                cursor.execute(
                    'INSERT INTO "tbl_Config_MaterialCategories" ("CategoryName") VALUES (%s)',
                    (category,)
                )
            cnx.commit()
            print(f"+ Initialized {len(MATERIAL_CATEGORIES)} material categories")
        else:
            print("- Material categories already exist")
    except Exception as err:
        print(f"X Failed to initialize material categories: {err}")
        cnx.rollback()
    
    # Initialize filler types
    try:
        cursor.execute('SELECT COUNT(*) FROM "tbl_Config_FillerTypes"')
        if cursor.fetchone()[0] == 0:
            for filler in FILLER_TYPES:
                cursor.execute(
                    'INSERT INTO "tbl_Config_FillerTypes" ("FillerTypeName") VALUES (%s)',
                    (filler,)
                )
            cnx.commit()
            print(f"+ Initialized {len(FILLER_TYPES)} filler types")
        else:
            print("- Filler types already exist")
    except Exception as err:
        print(f"X Failed to initialize filler types: {err}")
        cnx.rollback()
    
    # Initialize admin account
    try:
        cursor.execute('SELECT COUNT(*) FROM "tbl_Users" WHERE "Username" = %s', ('admin',))
        if cursor.fetchone()[0] == 0:
            try:
                # 安全说明：使用哈希密码存储（Bcrypt/Argon2）
                # 系统强制要求密码必须哈希存储，不支持明文密码
                from passlib.context import CryptContext
                
                # 尝试多种加密方式（优先 Argon2，兼容 Bcrypt）
                for schemes in [["bcrypt", "argon2"], ["bcrypt"], ["argon2"]]:
                    try:
                        pwd_context = CryptContext(schemes=schemes, deprecated="auto")
                        hashed_password = pwd_context.hash("admin123")
                        print(f"  Using password hash algorithm: {schemes[0]}")
                        print(f"  Password hash: {hashed_password[:50]}...")
                        break
                    except Exception:
                        continue
                else:
                    raise ImportError("No password hashing backend available")
                
            except ImportError as e:
                print(f"! Password hashing library not available")
                print(f"  Install: pip install passlib[argon2] bcrypt")
                raise
            
            cursor.execute(
                'INSERT INTO "tbl_Users" ("Username", "PasswordHash", "RealName", "Role", "IsActive") '
                'VALUES (%s, %s, %s, %s, %s)',
                ('admin', hashed_password, 'Administrator', 'admin', 1)
            )
            cnx.commit()
            print("+ Admin account created (admin/admin123)")
        else:
            print("- Admin account already exists")
    except ImportError:
        pass  # Already handled above
    except Exception as err:
        print(f"X Failed to create admin account: {err}")
        print(f"  Error details: {type(err).__name__}: {err}")
        cnx.rollback()
    
    cursor.close()
    cnx.close()
    
    print("\n" + "=" * 60)
    print("+ Initialization completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
