# Scripts 使用说明

本目录包含数据库初始化和大规模测试数据生成脚本。

## 目录脚本

- `create_tables.py`：创建数据库、建表、初始化基础配置与管理员账号。
- `generate_materials_fillers.py`：批量生成原料与填料数据（默认各 50 万）。
- `generate_test_data.py`：批量生成项目、配方组成和测试结果（默认 99 万项目）。

## 执行前准备

1. 进入后端目录：

```bash
cd backend_fastapi
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置环境变量文件 `env/.env.dev`，至少包含：

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_DATABASE=photopolymer_formulation_db
```

## 推荐执行顺序

1. 初始化数据库与表结构：

```bash
python scripts/create_tables.py
```

2. 生成原料和填料基础数据：

```bash
python scripts/generate_materials_fillers.py
```

3. 生成项目与测试结果数据：

```bash
python scripts/generate_test_data.py
```

## 关键说明

- 两个批量脚本会进行交互确认，输入 `yes` 或 `y` 才会继续执行。
- 批量生成数据量大，建议在性能较好的数据库环境运行。
- 生成脚本默认使用 `ENVIRONMENT=dev`。
- `generate_test_data.py` 依赖已有项目类型、原料、填料数据，建议严格按推荐顺序执行。
- 若库中已有同类数据，脚本不会自动清理旧数据；如需重建，请先自行清库或新建数据库。
