# 系统日志表创建指南

## 概述

系统日志功能包含两个核心表：
- **tbl_UserLoginLogs** - 用户登录日志表
- **tbl_UserRegistrationLogs** - 用户注册日志表

## 方法一：使用Python脚本（推荐）

### 运行脚本
```bash
cd backend_fastapi
python scripts/create_log_tables.py
```

### 脚本功能
- ✅ 自动连接到配置的数据库
- ✅ 创建日志表（如果不存在）
- ✅ 创建性能优化索引
- ✅ 验证表结构
- ✅ 显示详细的执行日志

## 方法二：使用SQL文件

### 直接执行SQL
```bash
mysql -u your_username -p your_database < sql/create_log_tables.sql
```

或在MySQL命令行中：
```sql
USE your_database;
SOURCE sql/create_log_tables.sql;
```

## 方法三：更新主创建脚本

如果是全新安装，运行主创建脚本即可自动创建所有表（包括日志表）：

```bash
cd scripts
python create_tables.py
```

## 表结构说明

### tbl_UserLoginLogs（用户登录日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| LogID | int(11) | 日志ID（主键，自增） |
| UserID | int(11) | 用户ID（外键） |
| Username | varchar(50) | 用户名 |
| LoginTime | datetime | 登录时间 |
| LogoutTime | datetime | 登出时间（可为空） |
| Duration | int(11) | 使用时长（秒，可为空） |
| IPAddress | varchar(50) | 登录IP地址 |
| UserAgent | text | 用户代理信息 |

**索引**：
- 主键索引：LogID
- 外键索引：UserID
- 普通索引：Username, LoginTime
- 复合索引：(UserID, LoginTime), Duration

### tbl_UserRegistrationLogs（用户注册日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| LogID | int(11) | 日志ID（主键，自增） |
| UserID | int(11) | 用户ID（外键） |
| Username | varchar(50) | 用户名 |
| RegistrationTime | datetime | 注册时间 |
| RealName | varchar(50) | 真实姓名 |
| Position | varchar(100) | 职位 |
| Email | varchar(100) | 邮箱 |
| Role | varchar(20) | 角色 |
| IPAddress | varchar(50) | 注册IP地址 |

**索引**：
- 主键索引：LogID
- 外键索引：UserID
- 普通索引：Username, RegistrationTime
- 复合索引：(UserID, RegistrationTime), Role

## 功能说明

### 自动日志记录

系统会在以下情况自动记录日志：

1. **用户登录** - 记录登录时间、IP、User-Agent
2. **用户注册** - 记录注册信息
3. **用户登出** - 更新登出时间和使用时长

### 统计功能

系统日志页面提供：
- 系统运行天数统计
- 今日登录次数和活跃用户数
- 今日总使用时长
- 登录日志查询（支持用户名、日期范围筛选）
- 注册日志查询（支持用户名、日期范围筛选）

## 验证安装

运行以下SQL验证表是否创建成功：

```sql
-- 查看表结构
SHOW CREATE TABLE tbl_UserLoginLogs;
SHOW CREATE TABLE tbl_UserRegistrationLogs;

-- 查看记录数
SELECT COUNT(*) FROM tbl_UserLoginLogs;
SELECT COUNT(*) FROM tbl_UserRegistrationLogs;

-- 查看索引
SHOW INDEX FROM tbl_UserLoginLogs;
SHOW INDEX FROM tbl_UserRegistrationLogs;
```

## 注意事项

1. **外键约束** - 日志表依赖 `tbl_Users` 表，请确保用户表已存在
2. **字符集** - 使用 `utf8mb4_unicode_ci` 排序规则
3. **级联删除** - 删除用户时会自动删除其相关日志
4. **性能优化** - 已为常用查询字段创建索引

## 故障排除

### 表已存在错误
如果收到"表已存在"错误，说明表已经创建，无需重复创建。

### 外键约束错误
确保 `tbl_Users` 表已经存在，并且 `UserID` 字段类型匹配。

### 权限错误
确保数据库用户有 `CREATE TABLE` 和 `CREATE INDEX` 权限。

## 后续步骤

创建日志表后：
1. 重启 FastAPI 后端服务
2. 访问系统日志页面（需要管理员权限）
3. 系统会自动开始记录日志

## 相关文件

- `backend_fastapi/app/api/v1/modules/logs/model.py` - 日志模型定义
- `backend_fastapi/app/api/v1/modules/logs/crud.py` - 日志CRUD操作
- `backend_fastapi/app/api/v1/modules/logs/controller.py` - 日志API路由
- `frontend_vue3/src/views/system/logs/index.vue` - 前端日志页面

