-- 设置用户为管理员
-- 使用方法: 在 MySQL 中执行此脚本

-- 1. 查看所有用户及其角色
SELECT UserID, Username, RealName, Role, IsActive FROM tbl_Users;

-- 2. 将指定用户名设置为管理员（修改 'your_username' 为实际用户名）
UPDATE tbl_Users 
SET Role = 'admin' 
WHERE Username = 'your_username';

-- 3. 或者将用户ID为1的用户设置为管理员
-- UPDATE tbl_Users 
-- SET Role = 'admin' 
-- WHERE UserID = 1;

-- 4. 验证更改
SELECT UserID, Username, RealName, Role FROM tbl_Users WHERE Role = 'admin';

