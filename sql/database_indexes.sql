-- 数据库性能优化 - 索引建议
-- 执行前请先备份数据库！
-- 根据查询模式添加索引可以显著提升性能

USE test_base;

-- ============================================
-- 用户表索引
-- ============================================

-- 用户名索引（已有UNIQUE约束会自动创建）
-- CREATE UNIQUE INDEX idx_users_username ON tbl_Users(Username);

-- 邮箱索引（用于查找）
CREATE INDEX IF NOT EXISTS idx_users_email ON tbl_Users(Email);

-- 角色索引（用于筛选管理员/普通用户）
CREATE INDEX IF NOT EXISTS idx_users_role ON tbl_Users(Role);

-- 活跃状态索引（用于筛选启用/禁用用户）
CREATE INDEX IF NOT EXISTS idx_users_is_active ON tbl_Users(IsActive);

-- 最后登录时间索引（用于查询活跃用户）
CREATE INDEX IF NOT EXISTS idx_users_last_login ON tbl_Users(LastLogin);

-- 复合索引：角色+活跃状态（常见组合查询）
CREATE INDEX IF NOT EXISTS idx_users_role_active ON tbl_Users(Role, IsActive);


-- ============================================
-- 项目信息表索引
-- ============================================

-- 项目类型外键索引（用于JOIN查询）
CREATE INDEX IF NOT EXISTS idx_project_type_fk ON tbl_ProjectInfo(ProjectType_FK);

-- 配方日期索引（用于按日期筛选）
CREATE INDEX IF NOT EXISTS idx_project_formulation_date ON tbl_ProjectInfo(FormulationDate);

-- 配方编码索引（已有UNIQUE约束会自动创建）
-- CREATE UNIQUE INDEX idx_project_formula_code ON tbl_ProjectInfo(FormulaCode);

-- 配方设计师索引（用于查找某人的所有配方）
CREATE INDEX IF NOT EXISTS idx_project_formulator ON tbl_ProjectInfo(FormulatorName);

-- 复合索引：类型+日期（常见组合查询）
CREATE INDEX IF NOT EXISTS idx_project_type_date ON tbl_ProjectInfo(ProjectType_FK, FormulationDate);


-- ============================================
-- 原料表索引
-- ============================================

-- 类别外键索引
CREATE INDEX IF NOT EXISTS idx_material_category_fk ON tbl_RawMaterials(Category_FK);

-- 供应商索引（用于按供应商查找）
CREATE INDEX IF NOT EXISTS idx_material_supplier ON tbl_RawMaterials(Supplier);

-- CAS号索引（用于化学品查找）
CREATE INDEX IF NOT EXISTS idx_material_cas ON tbl_RawMaterials(CAS_Number);

-- 商品名称索引（用于搜索）
CREATE INDEX IF NOT EXISTS idx_material_trade_name ON tbl_RawMaterials(TradeName);


-- ============================================
-- 无机填料表索引
-- ============================================

-- 填料类型外键索引
CREATE INDEX IF NOT EXISTS idx_filler_type_fk ON tbl_InorganicFillers(FillerType_FK);

-- 供应商索引
CREATE INDEX IF NOT EXISTS idx_filler_supplier ON tbl_InorganicFillers(Supplier);

-- 商品名称索引
CREATE INDEX IF NOT EXISTS idx_filler_trade_name ON tbl_InorganicFillers(TradeName);

-- 是否硅烷化索引（用于筛选）
CREATE INDEX IF NOT EXISTS idx_filler_silanized ON tbl_InorganicFillers(IsSilanized);


-- ============================================
-- 配方成分表索引
-- ============================================

-- 项目ID外键索引（非常重要！用于查找项目的所有成分）
CREATE INDEX IF NOT EXISTS idx_composition_project_fk ON tbl_FormulaComposition(ProjectID_FK);

-- 原料ID外键索引
CREATE INDEX IF NOT EXISTS idx_composition_material_fk ON tbl_FormulaComposition(MaterialID_FK);

-- 填料ID外键索引
CREATE INDEX IF NOT EXISTS idx_composition_filler_fk ON tbl_FormulaComposition(FillerID_FK);

-- 复合索引：项目+原料（避免重复添加）
CREATE INDEX IF NOT EXISTS idx_composition_project_material ON tbl_FormulaComposition(ProjectID_FK, MaterialID_FK);

-- 复合索引：项目+填料
CREATE INDEX IF NOT EXISTS idx_composition_project_filler ON tbl_FormulaComposition(ProjectID_FK, FillerID_FK);


-- ============================================
-- 测试结果表索引
-- ============================================

-- 喷墨测试结果
CREATE INDEX IF NOT EXISTS idx_test_ink_project_fk ON tbl_TestResults_Ink(ProjectID_FK);
CREATE INDEX IF NOT EXISTS idx_test_ink_date ON tbl_TestResults_Ink(TestDate);

-- 涂层测试结果
CREATE INDEX IF NOT EXISTS idx_test_coating_project_fk ON tbl_TestResults_Coating(ProjectID_FK);
CREATE INDEX IF NOT EXISTS idx_test_coating_date ON tbl_TestResults_Coating(TestDate);

-- 3D打印测试结果
CREATE INDEX IF NOT EXISTS idx_test_3d_project_fk ON tbl_TestResults_3DPrint(ProjectID_FK);
CREATE INDEX IF NOT EXISTS idx_test_3d_date ON tbl_TestResults_3DPrint(TestDate);

-- 复合材料测试结果
CREATE INDEX IF NOT EXISTS idx_test_composite_project_fk ON tbl_TestResults_Composite(ProjectID_FK);
CREATE INDEX IF NOT EXISTS idx_test_composite_date ON tbl_TestResults_Composite(TestDate);


-- ============================================
-- 全文搜索索引（可选，MySQL 5.6+）
-- ============================================

-- 项目名称全文搜索
-- ALTER TABLE tbl_ProjectInfo ADD FULLTEXT INDEX ft_project_name(ProjectName);

-- 原料商品名称和功能说明全文搜索
-- ALTER TABLE tbl_RawMaterials ADD FULLTEXT INDEX ft_material_search(TradeName, FunctionDescription);


-- ============================================
-- 查看索引使用情况
-- ============================================

-- 查看所有索引
-- SELECT 
--     TABLE_NAME, 
--     INDEX_NAME, 
--     SEQ_IN_INDEX, 
--     COLUMN_NAME,
--     INDEX_TYPE
-- FROM INFORMATION_SCHEMA.STATISTICS
-- WHERE TABLE_SCHEMA = 'test_base'
-- ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- 查看未使用的索引（需要运行一段时间后执行）
-- SELECT 
--     t.TABLE_SCHEMA,
--     t.TABLE_NAME,
--     t.INDEX_NAME
-- FROM information_schema.TABLES t
-- LEFT JOIN information_schema.STATISTICS s 
--     ON t.TABLE_SCHEMA = s.TABLE_SCHEMA 
--     AND t.TABLE_NAME = s.TABLE_NAME
-- WHERE t.TABLE_SCHEMA = 'test_base'
--     AND t.TABLE_TYPE = 'BASE TABLE'
--     AND s.INDEX_NAME IS NOT NULL;


-- ============================================
-- 性能监控查询
-- ============================================

-- 查看慢查询
-- SHOW FULL PROCESSLIST;

-- 查看表的统计信息
-- ANALYZE TABLE tbl_ProjectInfo;
-- ANALYZE TABLE tbl_RawMaterials;
-- ANALYZE TABLE tbl_InorganicFillers;
-- ANALYZE TABLE tbl_FormulaComposition;

-- 查看索引基数（Cardinality越高越好）
-- SHOW INDEX FROM tbl_ProjectInfo;


-- ============================================
-- 注意事项
-- ============================================

/*
1. 索引权衡：
   - 优点：加快查询速度
   - 缺点：占用额外存储空间，降低INSERT/UPDATE/DELETE速度
   
2. 索引选择原则：
   - 在WHERE、JOIN、ORDER BY中频繁使用的列
   - 高选择性的列（数据分布广，重复少）
   - 避免在小表上创建过多索引
   
3. 维护建议：
   - 定期执行ANALYZE TABLE更新统计信息
   - 监控慢查询日志
   - 使用EXPLAIN分析查询计划
   - 根据实际使用情况调整索引

4. 测试建议：
   - 在生产环境应用前，先在测试环境验证
   - 测试索引对写入性能的影响
   - 监控磁盘空间使用

5. 删除索引：
   -- DROP INDEX index_name ON table_name;
*/

