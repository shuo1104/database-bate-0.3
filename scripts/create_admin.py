"""
创建初始管理员账号脚本
运行此脚本可以创建一个默认的管理员账号
"""
import mysql.connector
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from argon2 import PasswordHasher
from config import DB_CONFIG

# 初始化密码哈希器
ph = PasswordHasher()

# 默认管理员账号信息
DEFAULT_ADMIN = {
    'username': 'admin',
    'password': 'admin123',  # 默认密码，首次登录后建议修改
    'real_name': '系统管理员',
    'position': '管理员',
    'role': 'admin',
    'email': 'admin@example.com'
}


def create_admin_user(username=None, password=None):
    """
    创建管理员账号
    
    Args:
        username: 用户名，默认为 'admin'
        password: 密码，默认为 'admin123'
    """
    admin_info = DEFAULT_ADMIN.copy()

    if username:
        admin_info['username'] = username
    if password:
        admin_info['password'] = password

    print("=" * 60)
    print("创建管理员账号")
    print("=" * 60)

    try:
        # 连接数据库
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor(dictionary=True)

        # 检查用户是否已存在
        cursor.execute("SELECT UserID, Username FROM tbl_Users WHERE Username = %s",
                       (admin_info['username'],))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"\n W:  用户 '{admin_info['username']}' 已存在！")
            print(f"   UserID: {existing_user['UserID']}")

            reset = input("\n是否重置该账号的密码？(y/n): ").strip().lower()
            if reset == 'y':
                password_hash = ph.hash(admin_info['password'])
                cursor.execute("""
                    UPDATE tbl_Users 
                    SET PasswordHash = %s, Role = 'admin', IsActive = 1
                    WHERE Username = %s
                """, (password_hash, admin_info['username']))
                cnx.commit()
                print(f"\n√ 用户 '{admin_info['username']}' 密码已重置为: {admin_info['password']}")
            else:
                print("\n操作已取消")
        else:
            # 生成密码哈希
            password_hash = ph.hash(admin_info['password'])

            # 插入管理员账号
            cursor.execute("""
                INSERT INTO tbl_Users 
                (Username, PasswordHash, RealName, Position, Role, Email, IsActive)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
            """, (
                admin_info['username'],
                password_hash,
                admin_info['real_name'],
                admin_info['position'],
                admin_info['role'],
                admin_info['email']
            ))
            cnx.commit()

            print(f"\n√ 管理员账号创建成功！")

        print("\n账号信息：")
        print(f"   用户名: {admin_info['username']}")
        print(f"   密码: {admin_info['password']}")
        print(f"   角色: 管理员")
        print(f"\nW:  请登录后立即修改密码！")

        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        print(f"\nX 数据库错误: {err}")
        return False
    except Exception as e:
        print(f"\nX 错误: {e}")
        return False

    print("=" * 60)
    return True


if __name__ == '__main__':
    create_admin_user()
