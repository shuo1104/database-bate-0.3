-- 修复日志表结构 - 添加缺失的字段
-- 执行方法: mysql -u root -p test_base < fix_log_tables.sql

USE test_base;

-- 检查并添加 IsOnline 字段
ALTER TABLE tbl_UserLoginLogs 
ADD COLUMN IF NOT EXISTS `IsOnline` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否在线（1:是，0:否）';

-- 检查并添加 LastHeartbeat 字段
ALTER TABLE tbl_UserLoginLogs 
ADD COLUMN IF NOT EXISTS `LastHeartbeat` datetime COMMENT '最后心跳时间';

-- 为 IsOnline 添加索引
CREATE INDEX IF NOT EXISTS `idx_login_is_online` ON tbl_UserLoginLogs(`IsOnline`);

-- 验证表结构
DESC tbl_UserLoginLogs;

SELECT '日志表结构已修复！' AS status;

