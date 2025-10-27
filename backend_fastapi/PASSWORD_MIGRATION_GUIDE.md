# 🔐 密码迁移指南

## 📋 **问题说明**

数据库中的密码可能是以下几种格式：
- 明文密码（不安全）
- Argon2 哈希（旧 Flask 系统）
- Bcrypt 哈希（新 FastAPI 系统）✅

为了统一和安全，我们需要将所有密码迁移为 **Bcrypt 哈希**。

---

## 🚀 **快速迁移（3 步）**

### **步骤 1：运行迁移脚本**

```bash
cd D:\WorkSpace\workspace\data_base\backend_fastapi
python migrate_passwords.py
```

### **步骤 2：选择操作**

脚本会显示菜单：
```
请选择操作：
  1. 迁移现有用户密码为 Bcrypt
  2. 添加测试用户（Bcrypt 密码）
  0. 退出
```

**输入 `1` 并按回车**

### **步骤 3：确认迁移**

脚本会询问确认：
```
⚠️  确认要迁移所有用户密码吗？[y/N]:
```

**输入 `y` 并按回车**

---

## 📊 **迁移过程示例**

```
==============================================================
  密码迁移工具
  将明文密码或 Argon2 密码迁移为 Bcrypt 哈希
==============================================================

📊 找到 3 个用户

处理用户: admin (ID: 1)
  🔄 迁移 - 检测到明文密码
  ✅ 成功 - 密码已更新为 Bcrypt 哈希
     旧密码（明文）: admin123
     新哈希: $2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxx...

处理用户: user1 (ID: 2)
  ⏭️  跳过 - 已经是 Bcrypt 格式

处理用户: testuser (ID: 3)
  ⚠️  警告 - 检测到 Argon2 哈希
     无法自动迁移（需要原始明文密码）
     建议用户重置密码或手动设置

==============================================================
  迁移完成
==============================================================
✅ 成功迁移: 1 个用户
⏭️  跳过: 2 个用户
❌ 错误: 0 个用户

🎉 密码迁移成功！用户可以使用原密码登录。
```

---

## 🎯 **迁移逻辑**

### 1. **明文密码** → ✅ **自动迁移**
```
明文密码: admin123
↓ 使用 Bcrypt 加密
新哈希: $2b$12$xxxxxxxxxxxxxxxxxxxx...
```
✅ 用户使用原密码 `admin123` 可以正常登录

### 2. **Bcrypt 哈希** → ⏭️ **跳过**
```
已经是 Bcrypt 格式: $2b$12$...
```
⏭️ 不需要迁移，保持不变

### 3. **Argon2 哈希** → ⚠️ **无法自动迁移**
```
Argon2 哈希: $argon2id$v=19$m=65536...
```
⚠️ 无法从哈希还原明文，需要手动处理

---

## 🔧 **手动处理 Argon2 密码**

### 方式 1：让用户重置密码（推荐）

实现密码重置功能，让用户输入新密码。

### 方式 2：手动更新（如果知道明文密码）

如果您知道某个用户的明文密码，可以手动更新：

```python
# 在 Python 中执行
from app.core.security import hash_password

# 生成新的 Bcrypt 哈希
username = "某用户"
plain_password = "原密码"  # 您知道的明文密码
new_hash = hash_password(plain_password)
print(f"新哈希: {new_hash}")

# 然后在数据库中执行
# UPDATE tbl_Users SET PasswordHash = '新哈希' WHERE Username = '某用户';
```

### 方式 3：直接在数据库中更新

```sql
-- 假设您知道用户的明文密码是 "password123"
-- 先在 Python 中生成哈希
-- 然后在数据库中更新

UPDATE tbl_Users 
SET PasswordHash = '$2b$12$生成的哈希值'
WHERE Username = '用户名';
```

---

## ✨ **添加测试用户**

### 运行脚本

```bash
python migrate_passwords.py
```

### 选择选项 2

```
请选择操作：
  1. 迁移现有用户密码为 Bcrypt
  2. 添加测试用户（Bcrypt 密码）  ← 选择这个
  0. 退出
```

### 输入用户信息

```
请输入用户名 [默认: testuser]: admin
请输入密码 [默认: test123]: admin123
```

### 结果

```
✅ 测试用户创建成功！
   用户名: admin
   密码: admin123
   角色: user
```

---

## 📝 **验证迁移结果**

### 方式 1：使用前端登录

1. 访问：http://localhost:3000
2. 使用迁移后的账号登录
3. 应该能成功登录 ✅

### 方式 2：查看数据库

```sql
SELECT 
    Username,
    LEFT(PasswordHash, 10) as HashPrefix,
    CASE 
        WHEN PasswordHash LIKE '$2b$%' THEN 'Bcrypt ✅'
        WHEN PasswordHash LIKE '$argon2%' THEN 'Argon2 ⚠️'
        WHEN PasswordHash LIKE '$%' THEN '其他哈希'
        ELSE '明文 ❌'
    END as PasswordType
FROM tbl_Users;
```

**期望结果**：所有用户都应该是 `Bcrypt ✅`

---

## 🔒 **安全建议**

### ✅ 迁移后
- 所有密码使用 Bcrypt 加密
- 安全性提升
- 统一密码存储格式

### ⚠️ 注意事项
1. **迁移前备份数据库**
   ```bash
   mysqldump -u root -p formulation_db > backup_before_migration.sql
   ```

2. **在测试环境先测试**
   - 确保迁移脚本正常工作
   - 验证用户能正常登录

3. **通知用户**
   - 如果有 Argon2 密码无法迁移
   - 通知这些用户重置密码

---

## 🐛 **常见问题**

### Q1: 迁移后用户无法登录？

**可能原因**：
1. 明文密码记录不正确
2. 数据库中密码已经被修改

**解决**：
```bash
# 重新创建用户或重置密码
python migrate_passwords.py
# 选择选项 2，创建新用户
```

### Q2: 有些用户是 Argon2 密码，怎么办？

**解决**：
1. 如果知道明文密码，手动更新
2. 让用户重置密码
3. 管理员手动设置新密码

### Q3: 迁移脚本报错？

**检查**：
1. 数据库连接是否正常
2. 后端服务是否已停止（避免冲突）
3. 查看详细错误信息

---

## 🎯 **快速命令**

```bash
# 迁移密码
cd backend_fastapi
python migrate_passwords.py

# 添加测试用户
python migrate_passwords.py
# 然后选择选项 2

# 测试登录
# 访问 http://localhost:3000
```

---

## ✅ **迁移完成后**

1. ✅ 重启后端服务
   ```bash
   python main.py run --env=dev
   ```

2. ✅ 测试登录
   - 使用原密码登录
   - 应该能成功 ✅

3. ✅ 删除明文密码记录（可选）
   - 如果您有备份，可以删除旧数据

---

**准备好开始迁移了吗？运行脚本吧！** 🚀

```bash
python migrate_passwords.py
```

