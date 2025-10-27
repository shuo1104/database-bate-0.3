#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动更新用户密码为 Bcrypt 哈希
用于 Argon2 密码的手动迁移
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.api.v1.modules.auth.model import UserModel
from app.core.security import hash_password
from app.core.logger import logger


async def update_user_password(username: str, plain_password: str):
    """
    更新指定用户的密码为 Bcrypt 哈希
    
    Args:
        username: 用户名
        plain_password: 明文密码
    """
    async with AsyncSessionLocal() as db:
        try:
            # 查找用户
            result = await db.execute(
                select(UserModel).where(UserModel.Username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ 用户 '{username}' 不存在")
                return False
            
            print(f"找到用户: {user.Username} (ID: {user.UserID})")
            print(f"当前密码哈希: {user.PasswordHash[:50]}...")
            
            # 生成新的 Bcrypt 哈希
            new_hash = hash_password(plain_password)
            print(f"新的 Bcrypt 哈希: {new_hash[:50]}...")
            
            # 更新密码
            await db.execute(
                update(UserModel)
                .where(UserModel.UserID == user.UserID)
                .values(PasswordHash=new_hash)
            )
            await db.commit()
            
            print(f"✅ 密码更新成功！")
            print(f"   用户名: {username}")
            print(f"   明文密码: {plain_password}")
            print(f"   现在可以使用此密码登录")
            
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"更新密码失败: {e}")
            print(f"❌ 更新失败: {e}")
            raise


async def batch_update():
    """批量更新多个用户的密码"""
    print("=" * 60)
    print("  批量更新用户密码")
    print("=" * 60)
    print()
    
    # 在这里添加需要更新的用户
    users_to_update = [
        {"username": "admin", "password": "admin123"},
        # 如果还有其他用户需要更新，请取消注释并修改
        # {"username": "user1", "password": "password1"},
        # {"username": "user2", "password": "password2"},
    ]
    
    success_count = 0
    fail_count = 0
    
    for user_data in users_to_update:
        username = user_data["username"]
        password = user_data["password"]
        
        print(f"\n处理用户: {username}")
        print("-" * 40)
        
        try:
            success = await update_user_password(username, password)
            if success:
                success_count += 1
            else:
                fail_count += 1
        except Exception:
            fail_count += 1
        
        print()
    
    print("=" * 60)
    print(f"✅ 成功: {success_count} 个用户")
    print(f"❌ 失败: {fail_count} 个用户")
    print("=" * 60)


async def interactive_update():
    """交互式更新单个用户密码"""
    print("=" * 60)
    print("  更新用户密码")
    print("=" * 60)
    print()
    
    username = input("请输入用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空")
        return
    
    password = input("请输入明文密码: ").strip()
    if not password:
        print("❌ 密码不能为空")
        return
    
    print()
    confirm = input(f"⚠️  确认要更新用户 '{username}' 的密码吗？[y/N]: ").strip().lower()
    
    if confirm == 'y':
        print()
        await update_user_password(username, password)
    else:
        print("❌ 已取消")


async def main():
    print("\n" + "=" * 60)
    print("  密码更新工具")
    print("  将 Argon2 密码手动更新为 Bcrypt")
    print("=" * 60)
    print()
    print("请选择操作：")
    print("  1. 交互式更新（输入用户名和密码）")
    print("  2. 批量更新（使用脚本中预设的用户列表）")
    print("  0. 退出")
    print()
    
    choice = input("请输入选项 [1]: ").strip() or "1"
    print()
    
    if choice == "1":
        await interactive_update()
    elif choice == "2":
        await batch_update()
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

