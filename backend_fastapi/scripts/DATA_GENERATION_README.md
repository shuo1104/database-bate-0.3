# 批量测试数据生成工具

## 概述

`generate_test_data.py` 是一个高性能的批量数据生成脚本，用于在 PostgreSQL 数据库中快速生成大量测试数据。

## 功能特性

- ✅ **高性能批量插入**：使用原生 SQL 批量插入，每秒可生成数千条记录
- ✅ **完整数据关联**：自动生成项目、配方组成、测试结果等关联数据
- ✅ **真实数据模拟**：使用随机但合理的数据值，符合实际业务场景
- ✅ **进度实时显示**：显示生成进度、速度和预计时间
- ✅ **数据分布均衡**：按项目类型均匀分配数据
- ✅ **事务安全**：批量提交，失败自动回滚

## 数据生成范围

### 默认生成 990,000 条项目记录

每个项目包含：
- **项目基本信息** (tbl_ProjectInfo)
  - 项目名称
  - 项目类型（喷墨/涂层/3D打印/复合材料）
  - 目标基材/应用领域
  - 配方设计师
  - 配方日期
  - 配方编码（自动生成）

- **配方组成** (tbl_FormulaComposition)
  - 每个项目 3-8 个成分
  - 包含原料或填料
  - 重量百分比（总和 100%）
  - 掺入方法
  - 备注信息

- **测试结果**（根据项目类型）
  - **喷墨** (tbl_TestResults_Ink)
    - 粘度、反应活性、粒径、表面张力、色度值
  - **涂层** (tbl_TestResults_Coating)
    - 附着力、透明度、表面硬度、耐化学性、成本估算
  - **3D打印** (tbl_TestResults_3DPrint)
    - 收缩率、杨氏模量、弯曲强度、邵氏硬度、抗冲击性
  - **复合材料** (tbl_TestResults_Composite)
    - 弯曲强度、杨氏模量、抗冲击性、转化率、吸水率

## 使用方法

### 前置条件

1. 数据库已创建并初始化（运行过 `create_tables.py`）
2. 已配置好数据库连接（`.env.dev` 文件）
3. 已安装所需依赖（`asyncpg`, `psycopg2-binary`, `sqlalchemy`）

### 运行脚本

```bash
cd backend_fastapi
python scripts/generate_test_data.py
```

### 交互确认

脚本会提示确认：
```
This will generate 990,000 test records. Continue? (yes/no):
```

输入 `yes` 或 `y` 开始生成。

### 执行过程

脚本会显示详细的执行信息：

```
================================================================================
BULK TEST DATA GENERATOR
================================================================================
Target: 990,000 project records
Batch size: 5,000
================================================================================

Loading reference data...
  + Loaded 4 project types
  + Loaded 15 materials
  + Loaded 12 fillers

Distribution:
  - 喷墨: 247,500 projects
  - 涂层: 247,500 projects
  - 3D打印: 247,500 projects
  - 复合材料: 247,500 projects

================================================================================
Starting data generation...
================================================================================

Processing: 喷墨 (247,500 records)
--------------------------------------------------------------------------------
  Batch 1/50: 5,000 records | Total: 5,000/990,000 (0.5%) | Rate: 1234 rec/s
  Batch 2/50: 5,000 records | Total: 10,000/990,000 (1.0%) | Rate: 1245 rec/s
  ...
```

## 性能指标

### 预期性能

- **生成速度**：约 1,000-2,000 条记录/秒（取决于硬件配置）
- **总耗时**：约 8-16 分钟生成 99 万条记录
- **批量大小**：5,000 条/批次（可在代码中调整）

### 数据量统计

| 数据类型 | 数量 | 说明 |
|---------|------|------|
| 项目记录 | 990,000 | 主表记录 |
| 配方组成 | ~4,000,000 | 每项目平均 4 个成分 |
| 测试结果 | 990,000 | 每项目 1 条测试结果 |
| **总计** | **~6,000,000** | **约 600 万条记录** |

## 自定义配置

### 修改生成数量

在脚本中修改 `total_projects` 参数：

```python
generator = BulkDataGenerator(total_projects=100000)  # 生成 10 万条
```

### 修改批量大小

在 `BulkDataGenerator` 类中修改：

```python
def __init__(self, total_projects: int = 990000):
    self.total_projects = total_projects
    self.batch_size = 10000  # 改为 1 万条/批次
```

### 修改数据模板

在 `DataTemplates` 类中自定义：
- `PROJECT_NAMES`: 项目名称前缀
- `FORMULATORS`: 配方设计师名单
- `SUBSTRATES`: 基材类型
- 等等...

## 注意事项

### ⚠️ 重要提醒

1. **数据库空间**：
   - 99 万条记录约占用 **500MB-1GB** 磁盘空间
   - 确保数据库有足够空间

2. **执行时间**：
   - 生成过程需要 **10-20 分钟**
   - 不要中途中断，否则可能产生不完整数据

3. **重复执行**：
   - 可以多次执行脚本
   - 每次执行会新增数据，不会删除现有数据
   - 如需清空重新生成，请先手动清空表

4. **数据库连接**：
   - 确保 PostgreSQL 服务正在运行
   - 确保连接配置正确

## 数据清理

如需清空测试数据重新生成：

```sql
-- 按顺序执行（由于外键约束）
TRUNCATE TABLE tbl_TestResults_Ink RESTART IDENTITY CASCADE;
TRUNCATE TABLE tbl_TestResults_Coating RESTART IDENTITY CASCADE;
TRUNCATE TABLE tbl_TestResults_3DPrint RESTART IDENTITY CASCADE;
TRUNCATE TABLE tbl_TestResults_Composite RESTART IDENTITY CASCADE;
TRUNCATE TABLE tbl_FormulaComposition RESTART IDENTITY CASCADE;
TRUNCATE TABLE tbl_ProjectInfo RESTART IDENTITY CASCADE;
```

或使用一条命令（PostgreSQL）：

```sql
TRUNCATE TABLE tbl_ProjectInfo RESTART IDENTITY CASCADE;
```

## 验证数据

生成完成后，脚本会自动验证记录数：

```sql
-- 手动验证
SELECT COUNT(*) FROM tbl_ProjectInfo;
SELECT COUNT(*) FROM tbl_FormulaComposition;
SELECT COUNT(*) FROM tbl_TestResults_Ink;
SELECT COUNT(*) FROM tbl_TestResults_Coating;
SELECT COUNT(*) FROM tbl_TestResults_3DPrint;
SELECT COUNT(*) FROM tbl_TestResults_Composite;
```

## 故障排除

### 问题：脚本无法连接数据库

**解决方案**：
- 检查 `.env.dev` 文件配置
- 确认 PostgreSQL 服务运行中
- 测试数据库连接：`python test_db.py`

### 问题：生成速度很慢

**可能原因**：
- 数据库在远程服务器（网络延迟）
- 磁盘 I/O 性能较低
- 数据库未优化

**优化建议**：
- 临时禁用索引，生成后重建
- 增加 PostgreSQL 的 `shared_buffers` 和 `work_mem`
- 使用 SSD 硬盘

### 问题：内存不足

**解决方案**：
- 减小 `batch_size`（如改为 2000）
- 分批次执行（先生成 50 万，再生成 50 万）

## 技术细节

### 批量插入优化

脚本使用 SQLAlchemy Core 的原生 SQL 批量插入：

```python
sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
await db.execute(text(sql), data)
```

这比 ORM 逐条插入快 **10-50 倍**。

### 外键关联

- 先插入父表（Projects）
- 获取生成的 ID
- 再插入子表（Compositions, TestResults）

### 数据一致性

- 配方组成的重量百分比总和 = 100%
- 每个项目只有一条测试结果（unique 约束）
- 日期范围：2020-01-01 至 2025-01-01（最近 5 年）

## 许可证

此脚本为项目内部工具，遵循项目主许可证。

---

**创建日期**: 2025-10-28  
**版本**: 1.0  
**作者**: System Generator

