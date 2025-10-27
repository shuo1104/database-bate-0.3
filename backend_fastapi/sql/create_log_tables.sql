-- ============================================
-- 系统日志表创建脚本
-- 用于记录用户登录、注册等系统日志
-- ============================================

-- 系统信息表
CREATE TABLE IF NOT EXISTS `tbl_SystemInfo` (
  `InfoID` int(11) NOT NULL AUTO_INCREMENT COMMENT '信息ID',
  `FirstStartTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '系统首次启动时间',
  `Version` varchar(50) COMMENT '系统版本',
  `LastUpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`InfoID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统信息表';

-- 用户登录日志表
CREATE TABLE IF NOT EXISTS `tbl_UserLoginLogs` (
  `LogID` int(11) NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `UserID` int(11) NOT NULL COMMENT '用户ID',
  `Username` varchar(50) NOT NULL COMMENT '用户名',
  `LoginTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
  `LogoutTime` datetime COMMENT '登出时间',
  `Duration` int(11) COMMENT '使用时长（秒）',
  `IPAddress` varchar(50) COMMENT '登录IP地址',
  `UserAgent` text COMMENT '用户代理信息',
  `IsOnline` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否在线（1:是，0:否）',
  `LastHeartbeat` datetime COMMENT '最后心跳时间',
  PRIMARY KEY (`LogID`),
  INDEX `idx_login_user_id` (`UserID`),
  INDEX `idx_login_username` (`Username`),
  INDEX `idx_login_time` (`LoginTime`),
  INDEX `idx_login_is_online` (`IsOnline`),
  INDEX `idx_login_user_time` (`UserID`, `LoginTime`),
  INDEX `idx_login_duration` (`Duration`),
  INDEX `idx_login_heartbeat` (`LastHeartbeat`),
  FOREIGN KEY (`UserID`) REFERENCES `tbl_Users` (`UserID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户登录日志表';

-- 用户注册日志表
CREATE TABLE IF NOT EXISTS `tbl_UserRegistrationLogs` (
  `LogID` int(11) NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `UserID` int(11) NOT NULL COMMENT '用户ID',
  `Username` varchar(50) NOT NULL COMMENT '用户名',
  `RegistrationTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `RealName` varchar(50) COMMENT '真实姓名',
  `Position` varchar(100) COMMENT '职位',
  `Email` varchar(100) COMMENT '邮箱',
  `Role` varchar(20) NOT NULL DEFAULT 'user' COMMENT '角色',
  `IPAddress` varchar(50) COMMENT '注册IP地址',
  PRIMARY KEY (`LogID`),
  INDEX `idx_reg_user_id` (`UserID`),
  INDEX `idx_reg_username` (`Username`),
  INDEX `idx_reg_time` (`RegistrationTime`),
  INDEX `idx_reg_user_time` (`UserID`, `RegistrationTime`),
  INDEX `idx_reg_role` (`Role`),
  FOREIGN KEY (`UserID`) REFERENCES `tbl_Users` (`UserID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户注册日志表';

-- 插入说明注释
SELECT '日志表创建完成！' AS Status;
SELECT COUNT(*) AS SystemInfoCount FROM tbl_SystemInfo;
SELECT COUNT(*) AS LoginLogCount FROM tbl_UserLoginLogs;
SELECT COUNT(*) AS RegistrationLogCount FROM tbl_UserRegistrationLogs;

