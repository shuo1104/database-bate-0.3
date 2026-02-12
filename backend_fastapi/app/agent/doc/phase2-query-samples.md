# Phase 2 Text-to-SQL 验证样例

本文档用于 Phase 2 端到端验证。覆盖成功查询、拦截规则、超时与只读约束。

## 前置条件

1. 已配置只读账号：`AGENT_DB_READONLY_USER=agent_readonly`。
2. 已配置白名单：`AGENT_SQL_ALLOWLIST_TABLES` 包含目标表。
3. 已完成数据库初始化并有基础样本数据。

## 成功样例

1. 查询单项目
   - 问题：`查询 ProjectID=1 的项目信息`
   - 预期：生成 `tbl_ProjectInfo` 的 `SELECT ... WHERE ... LIMIT ...`。

2. 查询项目配方组成
   - 问题：`查看项目 1 的原料与填料占比`
   - 预期：关联 `tbl_FormulaComposition`、`tbl_RawMaterials`、`tbl_InorganicFillers`，返回行数 >= 0。

3. 查询喷墨测试结果
   - 问题：`项目 1 的喷墨测试结果`
   - 预期：查询 `tbl_TestResults_Ink`，返回标准结构化结果。

4. 查询复合材料测试结果
   - 问题：`最近 10 条复合材料测试结果`
   - 预期：命中 `tbl_TestResults_Composite`，`LIMIT <= 10`。

5. 多表查询
   - 问题：`列出有测试结果的项目名称`
   - 预期：项目表与测试结果表关联查询，包含 WHERE 过滤。

## 失败样例（应被拦截）

6. 写操作
   - SQL：`UPDATE tbl_ProjectInfo SET ProjectName='x' WHERE ProjectID=1`
   - 预期：被安全层拦截（仅允许 SELECT）。

7. 非白名单表
   - SQL：`SELECT * FROM tbl_Users WHERE UserID=1`
   - 预期：被安全层拦截（表不在 allowlist）。

8. 无 WHERE 全表扫描
   - SQL：`SELECT * FROM tbl_ProjectInfo`
   - 预期：被安全层拦截（必须 WHERE）。

9. 过深子查询
   - SQL：三层以上 `IN (SELECT ... IN (SELECT ... IN (SELECT ...)))`
   - 预期：被安全层拦截（最大嵌套 2）。

10. 过多 UNION
    - SQL：`UNION` 超过 3 次
    - 预期：被安全层拦截。

## 超时与只读验证

1. 将 `AGENT_SQL_TIMEOUT` 临时设置为 1 秒，构造慢查询（例如大范围 join）。
   - 预期：返回超时错误。

2. 使用只读账号执行写 SQL（单独在 DB 客户端验证）。
   - 预期：数据库层面拒绝写操作。
