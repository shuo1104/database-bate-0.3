#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建系统日志表脚本
用于在现有数据库中添加日志表
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from sqlalchemy import text
from app.core.database import async_engine
from app.core.logger import logger


# 日志表创建SQL
LOG_TABLES_SQL = {
    'tbl_SystemInfo': """
        CREATE TABLE IF NOT EXISTS `tbl_SystemInfo` (
          `InfoID` int(11) NOT NULL AUTO_INCREMENT COMMENT '信息ID',
          `FirstStartTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '系统首次启动时间',
          `Version` varchar(50) COMMENT '系统版本',
          `LastUpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
          PRIMARY KEY (`InfoID`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统信息表'
    """,
    
    'tbl_UserLoginLogs': """
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
          FOREIGN KEY (`UserID`) REFERENCES `tbl_Users` (`UserID`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户登录日志表'
    """,
    
    'tbl_UserRegistrationLogs': """
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
          FOREIGN KEY (`UserID`) REFERENCES `tbl_Users` (`UserID`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户注册日志表'
    """
}

# 额外索引
EXTRA_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_login_user_time ON tbl_UserLoginLogs(UserID, LoginTime)",
    "CREATE INDEX IF NOT EXISTS idx_login_duration ON tbl_UserLoginLogs(Duration)",
    "CREATE INDEX IF NOT EXISTS idx_login_heartbeat ON tbl_UserLoginLogs(LastHeartbeat)",
    "CREATE INDEX IF NOT EXISTS idx_reg_user_time ON tbl_UserRegistrationLogs(UserID, RegistrationTime)",
    "CREATE INDEX IF NOT EXISTS idx_reg_role ON tbl_UserRegistrationLogs(Role)"
]


async def create_log_tables():
    """创建日志表"""
    logger.info("=" * 60)
    logger.info("开始创建系统日志表...")
    logger.info("=" * 60)
    
    async with async_engine.begin() as conn:
        # 创建表
        for table_name, create_sql in LOG_TABLES_SQL.items():
            try:
                logger.info(f"\n正在创建表: {table_name}")
                await conn.execute(text(create_sql))
                logger.info(f"✓ 表 {table_name} 创建成功")
            except Exception as e:
                if "already exists" in str(e).lower() or "table" in str(e).lower():
                    logger.info(f"- 表 {table_name} 已存在，跳过")
                else:
                    logger.error(f"✗ 表 {table_name} 创建失败: {str(e)}")
                    raise
        
        # 创建额外索引
        logger.info("\n正在创建性能优化索引...")
        for index_sql in EXTRA_INDEXES_SQL:
            try:
                index_name = index_sql.split("idx_")[1].split(" ")[0] if "idx_" in index_sql else "unknown"
                await conn.execute(text(index_sql))
                logger.info(f"✓ 索引 idx_{index_name} 创建成功")
            except Exception as e:
                if "duplicate" in str(e).lower() or "exists" in str(e).lower():
                    logger.info(f"- 索引 idx_{index_name} 已存在，跳过")
                else:
                    logger.warning(f"✗ 索引创建失败: {str(e)}")
        
        await conn.commit()
    
    logger.info("\n" + "=" * 60)
    logger.info("系统日志表创建完成！")
    logger.info("=" * 60)
    logger.info("\n已创建的表:")
    logger.info("  - tbl_SystemInfo (系统信息表)")
    logger.info("  - tbl_UserLoginLogs (用户登录日志表)")
    logger.info("  - tbl_UserRegistrationLogs (用户注册日志表)")
    logger.info("\n现在可以开始记录用户登录和注册日志了。")


async def verify_tables():
    """验证表是否创建成功"""
    logger.info("\n验证表结构...")
    
    async with async_engine.connect() as conn:
        for table_name in LOG_TABLES_SQL.keys():
            try:
                result = await conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                count = result.scalar()
                logger.info(f"✓ 表 {table_name} 存在，当前记录数: {count}")
            except Exception as e:
                logger.error(f"✗ 表 {table_name} 验证失败: {str(e)}")


async def main():
    """主函数"""
    try:
        await create_log_tables()
        await verify_tables()
        logger.info("\n✓ 所有操作完成！")
    except Exception as e:
        logger.error(f"\n✗ 创建日志表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

