# -*- coding: utf-8 -*-
"""
密码迁移脚本
将数据库中所有明文密码转换为哈希密码

使用方法:
    python scripts/migrate_passwords.py

功能:
    1. 扫描所有用户记录
    2. 识别明文密码（不以 $ 开头）
    3. 将明文密码转换为 Bcrypt 哈希
    4. 更新数据库记录
    5. 生成迁移报告
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_engine, AsyncSessionLocal
from app.core.security import hash_password
from app.api.v1.modules.auth.model import UserModel
from app.core.logger import logger


async def migrate_passwords():
    """
    迁移所有明文密码为哈希密码
    """
    print("\n" + "="*70)
    print("密码迁移工具 - 将明文密码转换为哈希密码")
    print("="*70 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. 统计所有用户数量
            result = await db.execute(select(func.count(UserModel.UserID)))
            total_users = result.scalar()
            print(f"📊 数据库中共有 {total_users} 个用户账号\n")
            
            if total_users == 0:
                print("✓ 数据库中没有用户，无需迁移")
                return
            
            # 2. 获取所有用户
            result = await db.execute(select(UserModel))
            users = result.scalars().all()
            
            # 3. 分析密码格式
            plaintext_users = []
            hashed_users = []
            
            for user in users:
                if user.PasswordHash and user.PasswordHash.startswith('$'):
                    hashed_users.append(user)
                else:
                    plaintext_users.append(user)
            
            print(f"✓ 已使用哈希密码的账号: {len(hashed_users)} 个")
            print(f"⚠ 使用明文密码的账号: {len(plaintext_users)} 个\n")
            
            if len(plaintext_users) == 0:
                print("="*70)
                print("✓ 所有用户密码均已哈希加密，无需迁移")
                print("="*70 + "\n")
                return
            
            # 4. 显示需要迁移的账号
            print("需要迁移的账号列表:")
            print("-" * 70)
            for i, user in enumerate(plaintext_users, 1):
                print(f"{i}. 用户名: {user.Username:20} | 角色: {user.Role:10} | "
                      f"明文密码: {user.PasswordHash[:20] if user.PasswordHash else 'None'}...")
            print("-" * 70 + "\n")
            
            # 5. 确认迁移
            print("⚠️  警告：此操作将修改数据库中的密码数据")
            print("   - 明文密码将被转换为 Bcrypt 哈希")
            print("   - 原始明文密码将无法恢复")
            print("   - 建议在执行前备份数据库\n")
            
            confirm = input("是否继续执行迁移？(yes/no): ").strip().lower()
            
            if confirm not in ['yes', 'y']:
                print("\n✗ 已取消迁移操作")
                return
            
            # 6. 执行迁移
            print("\n开始迁移密码...\n")
            migrated_count = 0
            failed_count = 0
            
            for user in plaintext_users:
                try:
                    # 保存原始明文密码（用于生成报告）
                    original_password = user.PasswordHash
                    
                    # 将明文密码转换为哈希
                    if original_password:
                        hashed_password = hash_password(original_password)
                        user.PasswordHash = hashed_password
                        
                        # 更新数据库
                        await db.flush()
                        
                        print(f"✓ 已迁移: {user.Username:20} | "
                              f"原密码: {original_password[:15]:15} | "
                              f"新哈希: {hashed_password[:30]}...")
                        migrated_count += 1
                    else:
                        print(f"⚠ 跳过: {user.Username:20} | 原因: 密码为空")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"✗ 失败: {user.Username:20} | 错误: {str(e)}")
                    failed_count += 1
                    logger.error(f"迁移user {user.Username} 密码failed: {e}")
            
            # 7. 提交事务
            await db.commit()
            
            # 8. 生成迁移报告
            print("\n" + "="*70)
            print("迁移完成报告")
            print("="*70)
            print(f"总用户数:       {total_users}")
            print(f"已哈希账号:     {len(hashed_users)} (无需迁移)")
            print(f"成功迁移:       {migrated_count}")
            print(f"迁移失败:       {failed_count}")
            print("="*70 + "\n")
            
            if migrated_count > 0:
                print("✓ 密码迁移成功完成！")
                print("\n📝 重要提醒:")
                print("   1. 所有明文密码已转换为 Bcrypt 哈希")
                print("   2. 用户使用原密码登录不受影响")
                print("   3. 系统现在强制要求哈希密码存储")
                print("   4. 建议通知用户定期修改密码\n")
            
        except Exception as e:
            await db.rollback()
            print(f"\n✗ 迁移过程发生错误: {e}")
            logger.error(f"密码迁移failed: {e}", exc_info=True)
            raise
        finally:
            await db.close()


async def verify_migration():
    """
    验证迁移结果
    """
    print("\n" + "="*70)
    print("验证迁移结果")
    print("="*70 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # 获取所有用户
            result = await db.execute(select(UserModel))
            users = result.scalars().all()
            
            plaintext_count = 0
            hashed_count = 0
            
            for user in users:
                if user.PasswordHash and user.PasswordHash.startswith('$'):
                    hashed_count += 1
                else:
                    plaintext_count += 1
                    print(f"⚠ 发现未迁移账号: {user.Username}")
            
            print(f"哈希密码账号: {hashed_count}")
            print(f"明文密码账号: {plaintext_count}\n")
            
            if plaintext_count == 0:
                print("✓ 验证通过：所有账号密码均已哈希加密")
            else:
                print("✗ 验证失败：仍有账号使用明文密码")
            
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"✗ 验证失败: {e}")
            logger.error(f"验证迁移resultfailed: {e}")


async def main():
    """主函数"""
    try:
        # 执行迁移
        await migrate_passwords()
        
        # 验证迁移结果
        await verify_migration()
        
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断操作")
    except Exception as e:
        print(f"\n✗ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

