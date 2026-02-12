# Advanced - PhotoPolymer 配方管理系统

一个基于 **FastAPI + Vue 3** 的现代化光敏聚合物配方管理系统。

## 📋 项目简介

本系统专为光敏聚合物材料研发设计，提供完整的配方管理、原料管理、测试结果记录等功能。采用前后端分离架构，支持多用户协作和权限管理。

## ✨ 主要功能

- 🔐 **用户认证**：JWT 令牌认证，支持管理员和普通用户角色
- 📊 **项目管理**：项目创建、编辑、查询，支持多种项目类型（喷墨、涂层、3D打印、复合材料）
- 🧪 **配方管理**：配方组成管理，原料和填料配比
- 📈 **测试结果**：多种测试指标录入和管理
- 🎨 **数据可视化**：测试结果图表导出
- 📝 **系统日志**：登录日志、操作日志记录
- 👥 **用户管理**：用户创建、编辑、权限管理（管理员功能）

## 🛠️ 技术栈

### 后端
- **框架**：FastAPI 0.104+
- **数据库**：PostgreSQL 14+
- **ORM**：SQLAlchemy 2.0（异步）
- **认证**：JWT (python-jose)
- **密码加密**：Passlib + Bcrypt
- **图表生成**：Matplotlib + Pillow

### 前端
- **框架**：Vue 3.5+
- **语言**：TypeScript 5.0+
- **构建工具**：Vite 6.0+
- **UI 组件**：Element Plus 2.10+
- **CSS 框架**：UnoCSS
- **状态管理**：Pinia
- **路由**：Vue Router 4
- **HTTP 客户端**：Axios

## 📦 项目结构

```
data_base/
├── backend_fastapi/          # 后端服务
│   ├── app/
│   │   ├── api/v1/          # API 路由
│   │   ├── core/            # 核心功能
│   │   ├── config/          # 配置文件
│   │   └── utils/           # 工具函数
│   ├── scripts/             # 数据库脚本
│   ├── logs/                # 日志文件
│   ├── main.py              # 应用入口
│   └── requirements.txt     # Python 依赖
│
├── frontend_vue3/           # 前端应用
│   ├── src/
│   │   ├── api/            # API 接口
│   │   ├── components/     # 公共组件
│   │   ├── layouts/        # 布局组件
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   └── views/          # 页面组件
│   ├── package.json        # 依赖配置
│   └── vite.config.ts      # Vite 配置
│
└── README.md               # 项目文档
```

## 🚀 快速开始

### 环境要求

- **Python**：3.9+
- **Node.js**：18+
- **PostgreSQL**：14+
- **pnpm**：8+ （推荐）或 npm

### 环境与部署原则

- 统一使用 **conda 的 `database` 虚拟环境** 进行后端开发、脚本执行与部署运维。
- 所有配置与部署操作遵守 **“更换生成服务器环境后能快速移植部署”** 的原则，避免写死本机路径与主机特定配置。

### 1. 克隆项目

```bash
git clone <repository-url>
cd data_base
```

### 2. 后端配置

```bash
# 进入后端目录
cd backend_fastapi

# 激活 conda 环境（统一使用 database）
conda activate database

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 编辑 env/.env.dev 文件，设置 PostgreSQL 连接信息
```

**env/.env.dev 配置示例：**

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_DATABASE=photopolymer_db

# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. 初始化数据库

```bash
# 创建数据库表
cd backend_fastapi
python scripts/create_tables.py

# 脚本会自动创建所有表和默认管理员账号
```

### 4. 启动后端服务

```bash
cd backend_fastapi
python main.py
```

后端服务将在 `http://localhost:8000` 运行

API 文档：`http://localhost:8000/docs`

### 5. 前端配置

```bash
# 进入前端目录
cd frontend_vue3

# 安装依赖
pnpm install
# 或
npm install

# 启动开发服务器
pnpm dev
# 或
npm run dev
```

前端应用将在 `http://localhost:3000` 运行

### 6. 默认账号

```
用户名：admin
密码：admin123
```

⚠️ **生产环境请立即修改默认密码！**

## 📚 功能模块

### 用户管理
- 用户登录/登出
- 个人信息编辑
- 密码修改
- 用户列表管理（管理员）
- 角色权限管理（管理员）

### 项目管理
- 项目创建和编辑
- 项目列表查询
- 项目详情查看
- 配方组成管理
- 测试结果录入
- 项目报告导出（图片）

### 原料管理
- 原料信息维护
- 原料列表查询
- 供应商信息管理

### 填料管理
- 填料信息维护
- 填料列表查询
- 填料属性管理

### 测试结果
- 支持多种项目类型的测试指标：
  - **喷墨**：粘度、反应活性、粒径、表面张力、色度值
  - **涂层**：附着力、透明度、表面硬度、耐化学性、成本
  - **3D打印**：收缩率、杨氏模量、弯曲强度、邵氏硬度、抗冲击性
  - **复合材料**：弯曲强度、杨氏模量、抗冲击性、转化率、吸水率

### 系统日志
- 登录日志记录
- 系统操作统计
- 用户活动监控（管理员）

## 🔧 开发指南

### 后端开发

后端采用分层架构：

```
模块/
├── model.py       # ORM 模型（数据库表定义）
├── schema.py      # Pydantic 模型（请求/响应验证）
├── crud.py        # 数据访问层（数据库操作）
├── service.py     # 业务逻辑层（核心业务逻辑）
└── controller.py  # 控制器层（HTTP 路由）
```

### 前端开发

前端使用 Vue 3 组合式 API：

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'

const data = ref([])

onMounted(async () => {
  // 调用 API
})
</script>
```

### API 调用示例

```typescript
import { getProjectListApi } from '@/api/projects'

// 获取项目列表
const response = await getProjectListApi({
  page: 1,
  page_size: 20
})
```

## 📊 数据生成

项目提供了批量测试数据生成脚本：

```bash
cd backend_fastapi

# 生成 99 万条项目记录（包含配方和测试结果）
python scripts/generate_test_data.py

# 生成原料和填料数据（各 50 万条）
python scripts/generate_materials_fillers.py
```

详细说明请查看：`backend_fastapi/scripts/DATA_GENERATION_README.md`

## 📝 日志系统

### 日志文件
- 日志按日期自动轮转（每天午夜）
- 当前日志：`logs/app.log` / `logs/error.log`
- 历史日志：`logs/app.log.2025-10-29` / `logs/error.log.2025-10-29`

### 日志配置
- 保留天数通过 `LOG_BACKUP_COUNT` 配置（默认 10 天）
- 自动清理过期日志
- 错误日志单独存储便于排查

## 🐛 常见问题

### 后端启动失败

1. 检查 Python 版本是否 >= 3.9
2. 检查 PostgreSQL 服务是否运行
3. 检查数据库连接配置是否正确
4. 检查端口 8000 是否被占用

### 前端启动失败

1. 检查 Node.js 版本是否 >= 18
2. 删除 `node_modules` 和 `pnpm-lock.yaml`，重新安装
3. 检查端口 3000 是否被占用

### 登录失败

1. 确认数据库已初始化（运行 `create_tables.py`）
2. 检查用户名和密码是否正确
3. 查看浏览器控制台和后端日志

### 跨域问题

1. 确保后端 CORS 配置包含前端地址
2. 检查前端 API 基础地址配置

### 端口修改

详细的端口配置说明请参考：[端口配置指南](./PORT_CONFIGURATION_GUIDE.md)

## 🔒 安全建议

- ✅ 生产环境修改默认管理员密码
- ✅ 使用强密码策略
- ✅ 定期备份数据库
- ✅ 启用 HTTPS（生产环境）
- ✅ 限制管理员账号数量
- ✅ 定期查看系统日志

## 📄 许可证

MIT License

## 👥 关于

**Advanced** - 专注于光敏聚合物材料研发的高新技术企业

---

**版本**：1.0.0  
**最后更新**：2025年10月29日
