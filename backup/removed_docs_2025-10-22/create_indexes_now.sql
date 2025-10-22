-- 立即创建所有性能索引

USE test_base;

-- 项目信息表索引
CREATE INDEX IF NOT EXISTS idx_project_type_fk ON tbl_ProjectInfo(ProjectType_FK);
CREATE INDEX IF NOT EXISTS idx_project_formulation_date ON tbl_ProjectInfo(FormulationDate);
CREATE INDEX IF NOT EXISTS idx_project_formulator ON tbl_ProjectInfo(FormulatorName);
CREATE INDEX IF NOT EXISTS idx_project_type_date ON tbl_ProjectInfo(ProjectType_FK, FormulationDate);

-- 原料表索引
CREATE INDEX IF NOT EXISTS idx_material_category_fk ON tbl_RawMaterials(Category_FK);
CREATE INDEX IF NOT EXISTS idx_material_supplier ON tbl_RawMaterials(Supplier);
CREATE INDEX IF NOT EXISTS idx_material_cas ON tbl_RawMaterials(CAS_Number);
CREATE INDEX IF NOT EXISTS idx_material_trade_name ON tbl_RawMaterials(TradeName);

-- 无机填料表索引
CREATE INDEX IF NOT EXISTS idx_filler_type_fk ON tbl_InorganicFillers(FillerType_FK);
CREATE INDEX IF NOT EXISTS idx_filler_supplier ON tbl_InorganicFillers(Supplier);
CREATE INDEX IF NOT EXISTS idx_filler_trade_name ON tbl_InorganicFillers(TradeName);
CREATE INDEX IF NOT EXISTS idx_filler_silanized ON tbl_InorganicFillers(IsSilanized);

-- 配方成分表索引（非常重要！）
CREATE INDEX IF NOT EXISTS idx_composition_project_fk ON tbl_FormulaComposition(ProjectID_FK);
CREATE INDEX IF NOT EXISTS idx_composition_material_fk ON tbl_FormulaComposition(MaterialID_FK);
CREATE INDEX IF NOT EXISTS idx_composition_filler_fk ON tbl_FormulaComposition(FillerID_FK);
CREATE INDEX IF NOT EXISTS idx_composition_project_material ON tbl_FormulaComposition(ProjectID_FK, MaterialID_FK);
CREATE INDEX IF NOT EXISTS idx_composition_project_filler ON tbl_FormulaComposition(ProjectID_FK, FillerID_FK);

-- 测试结果表索引
CREATE INDEX IF NOT EXISTS idx_test_ink_project_fk ON tbl_TestResults_Ink(ProjectID_FK);
CREATE INDEX IF NOT EXISTS idx_test_ink_date ON tbl_TestResults_Ink(TestDate);

CREATE INDEX IF NOT EXISTS idx_test_coating_project_fk ON tbl_TestResults_Coating(ProjectID_FK);
CREATE INDEX IF NOT EXISTS idx_test_coating_date ON tbl_TestResults_Coating(TestDate);

CREATE INDEX IF NOT EXISTS idx_test_3d_project_fk ON tbl_TestResults_3DPrint(ProjectID_FK);
CREATE INDEX IF NOT EXISTS idx_test_3d_date ON tbl_TestResults_3DPrint(TestDate);

CREATE INDEX IF NOT EXISTS idx_test_composite_project_fk ON tbl_TestResults_Composite(ProjectID_FK);
CREATE INDEX IF NOT EXISTS idx_test_composite_date ON tbl_TestResults_Composite(TestDate);

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_email ON tbl_Users(Email);
CREATE INDEX IF NOT EXISTS idx_users_role ON tbl_Users(Role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON tbl_Users(IsActive);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON tbl_Users(LastLogin);
CREATE INDEX IF NOT EXISTS idx_users_role_active ON tbl_Users(Role, IsActive);

SELECT 'Indexes created successfully!' as Status;


