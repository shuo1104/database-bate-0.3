#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
密码迁移脚本
将数据库中的明文密码或 Argon2 密码迁移为 Bcrypt 哈希
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.api.v1.modules.auth.model import UserModel
from app.core.security import hash_password
from app.core.logger import logger


async def migrate_passwords():
    """迁移所有用户密码为 Bcrypt 哈希"""
    
    print("=" * 60)
    print("  密码迁移工具")
    print("  将明文密码或 Argon2 密码迁移为 Bcrypt 哈希")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        try:
            # 查询所有用户
            result = await db.execute(select(UserModel))
            users = result.scalars().all()
            
            if not users:
                print("❌ 数据库中没有用户")
                return
            
            print(f"📊 找到 {len(users)} 个用户\n")
            
            # 统计信息
            migrated_count = 0
            skipped_count = 0
            error_count = 0
            
            for user in users:
                print(f"处理用户: {user.Username} (ID: {user.UserID})")
                
                # 检查密码格式
                password_hash = user.PasswordHash
                
                # 如果已经是 Bcrypt 格式，跳过
                if password_hash.startswith('$2b$') or password_hash.startswith('$2a$'):
                    print(f"  ⏭️  跳过 - 已经是 Bcrypt 格式")
                    skipped_count += 1
                    continue
                
                # 如果是 Argon2 格式
                if password_hash.startswith('$argon2'):
                    print(f"  ⚠️  警告 - 检测到 Argon2 哈希")
                    print(f"     无法自动迁移（需要原始明文密码）")
                    print(f"     建议用户重置密码或手动设置")
                    skipped_count += 1
                    continue
                
                # 如果是明文密码（不以 $ 开头）
                if not password_hash.startswith('$'):
                    print(f"  🔄 迁移 - 检测到明文密码")
                    plain_password = password_hash
                    
                    # 生成 Bcrypt 哈希
                    new_hash = hash_password(plain_password)
                    
                    # 更新数据库
                    await db.execute(
                        update(UserModel)
                        .where(UserModel.UserID == user.UserID)
                        .values(PasswordHash=new_hash)
                    )
                    
                    print(f"  ✅ 成功 - 密码已更新为 Bcrypt 哈希")
                    print(f"     旧密码（明文）: {plain_password}")
                    print(f"     新哈希: {new_hash[:50]}...")
                    migrated_count += 1
                else:
                    # 未知格式
                    print(f"  ❌ 错误 - 未知的密码格式: {password_hash[:30]}...")
                    error_count += 1
                
                print()
            
            # 提交更改
            await db.commit()
            
            # 显示统计
            print("=" * 60)
            print("  迁移完成")
            print("=" * 60)
            print(f"✅ 成功迁移: {migrated_count} 个用户")
            print(f"⏭️  跳过: {skipped_count} 个用户")
            print(f"❌ 错误: {error_count} 个用户")
            print()
            
            if migrated_count > 0:
                print("🎉 密码迁移成功！用户可以使用原密码登录。")
            
            if skipped_count > 0 and any(u.PasswordHash.startswith('$argon2') for u in users):
                print()
                print("⚠️  注意：Argon2 密码无法自动迁移")
                print("   建议这些用户重置密码或手动更新")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"密码迁移失败: {e}")
            print(f"\n❌ 迁移失败: {e}")
            raise


async def add_test_user():
    """添加一个测试用户（带 Bcrypt 密码）"""
    
    print("=" * 60)
    print("  添加测试用户")
    print("=" * 60)
    print()
    
    username = input("请输入用户名 [默认: testuser]: ").strip() or "testuser"
    password = input("请输入密码 [默认: test123]: ").strip() or "test123"
    
    async with AsyncSessionLocal() as db:
        try:
            # 检查用户是否存在
            result = await db.execute(
                select(UserModel).where(UserModel.Username == username)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"\n⚠️  用户 '{username}' 已存在")
                update_choice = input("是否更新密码？[y/N]: ").strip().lower()
                
                if update_choice == 'y':
                    # 更新密码
                    new_hash = hash_password(password)
                    await db.execute(
                        update(UserModel)
                        .where(UserModel.UserID == existing_user.UserID)
                        .values(PasswordHash=new_hash)
                    )
                    await db.commit()
                    print(f"✅ 密码已更新")
                    print(f"   用户名: {username}")
                    print(f"   密码: {password}")
                else:
                    print("❌ 已取消")
                return
            
            # 创建新用户
            from datetime import datetime
            new_user = UserModel(
                Username=username,
                PasswordHash=hash_password(password),
                Role="user",
                IsActive=True,
                CreatedAt=datetime.now()
            )
            
            db.add(new_user)
            await db.commit()
            
            print(f"\n✅ 测试用户创建成功！")
            print(f"   用户名: {username}")
            print(f"   密码: {password}")
            print(f"   角色: user")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"创建用户失败: {e}")
            print(f"\n❌ 创建失败: {e}")
            raise


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  密码管理工具")
    print("=" * 60)
    print()
    print("请选择操作：")
    print("  1. 迁移现有用户密码为 Bcrypt")
    print("  2. 添加测试用户（Bcrypt 密码）")
    print("  0. 退出")
    print()
    
    choice = input("请输入选项 [1]: ").strip() or "1"
    print()
    
    if choice == "1":
        confirm = input("⚠️  确认要迁移所有用户密码吗？[y/N]: ").strip().lower()
        if confirm == 'y':
            await migrate_passwords()
        else:
            print("❌ 已取消")
    elif choice == "2":
        await add_test_user()
    elif choice == "0":
        print("👋 再见！")
    else:
        print("❌ 无效的选项")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

