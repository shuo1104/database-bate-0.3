# TODO 清单 — Agent 系统

本清单基于 `implementation-steps.md` 生成，用于跟踪构建进度。

> **环境约定**：统一使用 conda 的 `database` 虚拟环境；一切遵守"更换生产服务器后能快速移植部署"的原则——密钥走 `.env`、路径用相对路径、依赖锁 `requirements.txt`、DDL 走 Alembic 迁移。
>
> **阶段约定**：每个 Phase 可独立交付验证，不存在对后续 Phase 的前置依赖。

---

## Phase 0 — 基线搭建与 Agent 骨架

### 依赖与包结构

- [ ] 在 `backend_fastapi/requirements.txt` 中追加依赖：
  - [ ] `langchain>=0.2`
  - [ ] `langchain-openai>=0.1`
  - [ ] `openai>=1.0`
- [ ] 创建 `agent/` 完整包目录结构，每个目录含 `__init__.py`：
  - [ ] `agent/__init__.py`
  - [ ] `agent/config/__init__.py`
  - [ ] `agent/core/__init__.py`
  - [ ] `agent/tools/__init__.py`
  - [ ] `agent/tools/etl/__init__.py`
  - [ ] `agent/tools/sql/__init__.py`
  - [ ] `agent/tools/ml/__init__.py`
  - [ ] `agent/schemas/__init__.py`
  - [ ] `agent/api/__init__.py`
  - [ ] `agent/tests/__init__.py`

### 配置集成

- [ ] 在 `app/config/settings.py` 中新增 Agent 相关配置字段：
  - [ ] `DEEPSEEK_API_KEY`
  - [ ] `DEEPSEEK_BASE_URL`（默认 `https://api.deepseek.com/v1`）
  - [ ] `DEEPSEEK_MODEL`（默认模型名称）
  - [ ] `MINERU_API_URL`
  - [ ] `AGENT_SQL_TIMEOUT`（默认 10 秒）
  - [ ] `AGENT_SQL_ALLOWLIST_TABLES`（白名单表列表）
- [ ] 更新 `backend_fastapi/env/env.example`，补充上述变量模板。
- [ ] 在 `agent/config/` 下创建策略配置（引用 `settings` 全局实例）：
  - [ ] Deepseek LLM 参数（temperature、max_tokens 等）
  - [ ] SQL 安全策略（白名单表、超时、最大重试次数）
  - [ ] MinerU API 参数

### 数据库准备

- [ ] 定义 Agent 相关 ORM 模型（遵循项目现有 `model.py` 惯例）：
  - [ ] `AgentTask` — 异步任务跟踪（任务 ID、类型、状态、结果、创建/完成时间）
  - [ ] `AgentIngestRecord` — 摄取记录（原始文件路径、提取字段、置信度、审核状态、溯源信息）
  - [ ] `AgentAuditLog` — Agent 操作审计日志（用户、操作类型、工具链路、耗时）
- [ ] 生成 Alembic 迁移文件并执行，确认表创建成功。
- [ ] 创建 PostgreSQL 只读角色（`agent_readonly`），仅授予 SELECT 权限于白名单表。在 `scripts/` 下新增初始化 SQL 脚本。

### Agent 骨架

- [ ] 验证 Deepseek API 连通性（通过 OpenAI SDK，配置 `base_url`）。
- [ ] 在 `agent/core/` 中初始化 LangChain ReAct Agent（暂无业务 Tool），验证空对话循环正常运行。
- [ ] 在 `agent/schemas/` 中定义 Pydantic 基础模型：
  - [ ] 摄取输出 Schema
  - [ ] 查询请求/响应 Schema
- [ ] 建立 `agent/tests/` 基础测试框架，包含 LLM Mock 辅助工具。

---

## Phase 1 — 文档摄取（MinerU + ETL）

### API 端点（摄取、任务、审核）

- [ ] 在 `app/api/v1/modules/` 下创建 `agent` 模块（Controller → Service 分层，遵循项目惯例）。
- [ ] 实现端点：
  - [ ] `POST /api/v1/agent/ingest` — 提交文件摄取任务，立即返回任务 ID。
  - [ ] `GET /api/v1/agent/tasks/{id}` — 查询异步任务状态与结果。
  - [ ] `GET /api/v1/agent/review` — 获取待人工审核的摄取记录列表。
  - [ ] `PUT /api/v1/agent/review/{id}` — 提交审核结果（通过 / 拒绝 / 修改字段值）。
- [ ] 在 `app/api/v1/__init__.py` 中注册 agent 路由。

### 摄取管线

- [ ] 文件接收：支持 PDF / 图片 / CSV 上传，存储原始文件并写入 `AgentTask` 记录。
- [ ] 调用 MinerU API 进行 OCR / PDF 解析，获取原始文本或半结构化内容。
- [ ] 将 MinerU 输出送入 Deepseek，通过 Prompt 提取为目标 JSON Schema。
- [ ] 对提取字段做类型检查、范围校验，为每个字段标记置信度分数。
- [ ] 低置信度处理：低于阈值的记录以 `pending_review` 状态写入 `AgentIngestRecord`。
- [ ] 校验通过的数据通过 SQLAlchemy 异步会话写入 PostgreSQL，记录溯源信息。
- [ ] 将摄取能力封装为 LangChain Tool 并注册到 Agent。

### 异步执行

- [ ] 使用 FastAPI BackgroundTasks 异步执行 OCR + LLM 管线。
- [ ] `POST /api/v1/agent/ingest` 立即返回任务 ID，前端通过 `GET /api/v1/agent/tasks/{id}` 轮询。

> **局限性说明**：BackgroundTasks 无持久化，服务重启后进行中的任务会丢失，且无内置重试机制。MVP 阶段可接受；生产环境如需可靠性保证，后续考虑迁移至 Celery + Redis。

---

## Phase 2 — 结构化查询（Text-to-SQL）

- [ ] Schema Grounding：将目标表结构信息（表名、字段、类型、示例值）注入 Prompt。
  - [ ] 目标表：projects、materials、fillers、test_results 及关联关系。
- [ ] SQL 安全层：
  - [ ] 仅允许查询白名单表。
  - [ ] 禁止 DDL 和 DML（INSERT / UPDATE / DELETE）。
  - [ ] 拒绝子查询嵌套 > 2 层、UNION > 3 条、无 WHERE 全表扫描。
  - [ ] 查询执行硬超时 10 秒。
- [ ] 使用 `agent_readonly` 只读角色执行 SQL，从数据库层面杜绝写操作。
- [ ] 自纠错循环：SQL 执行失败时反馈错误给 Deepseek 重新生成，最多重试 2 次。
- [ ] 结果格式化为用户友好的文本或表格形式。
- [ ] 将 Text-to-SQL 封装为 LangChain Tool 并注册到 Agent。

---

## Phase 3 — ML 推理（占位预留）

- [ ] 在 `agent/tools/ml/` 下建立目录结构（仅 `__init__.py`）。
- [ ] 在 `agent/schemas/` 中定义 ML 输入输出 Schema（特征字段、预测结果、置信度）。
- [ ] 预留 LangChain Tool 注册入口，待模型接口就绪后接入。

---

## Phase 4 — Chat 端点与生产加固

### Chat 端点

- [ ] 实现 `POST /api/v1/agent/chat` — 发送用户查询（文本 + 可选文件），返回 Agent 响应。
  - [ ] Agent 根据意图自动选择工具（摄取 / 查询），信息不足时主动追问。

### 认证与权限

- [ ] 所有 Agent 端点纳入现有 JWT 认证体系。
- [ ] 在 `agent/config/` 中定义角色权限（谁可使用 Agent、谁可审核数据）。
- [ ] SQL 查询结果注入用户数据权限（通过 WHERE 条件限定当前用户的项目范围）。

### 日志与审计

- [ ] 通过 LangChain Callback 记录完整工具链路（用户输入、工具选择、参数、输出、耗时）。
- [ ] 关键操作（数据入库、审核通过）写入 `AgentAuditLog` 表供审计。

### 错误处理与降级

- [ ] Deepseek API 超时/不可用 → 返回友好错误提示。
- [ ] MinerU API 异常 → 记录原始文件，标记任务为 `failed`，支持重试。
- [ ] SQL 执行异常 → 已在 Phase 2 自纠错循环中覆盖。

### 应用启动集成

- [ ] 如 Agent 有初始化逻辑（如预加载 Schema Grounding 数据），接入 `plugin/init_app.py` 的应用生命周期。
- [ ] 确认 Agent 端点是否需要加入 `TOKEN_REQUEST_PATH_EXCLUDE` 白名单（通常不需要，所有端点都应鉴权）。

---

## Phase 5 — 前端 Agent 浮动面板

### API 层（`frontend_vue3/src/api/agent.ts`）

- [ ] 参照现有 `api/projects.ts` 模式，使用 `request<T>()` 封装。
- [ ] 定义 TypeScript 接口：`AgentTaskSubmitResponse`、`AgentTaskResponse`、`AgentReviewListResponse`、`AgentReviewUpdateRequest`、`AgentChatRequest`、`AgentChatResponse`。
- [ ] 实现 API 函数：
  - [ ] `submitIngestApi(file: File)` → `POST /agent/ingest`（multipart/form-data）
  - [ ] `getTaskStatusApi(taskId: number)` → `GET /agent/tasks/{id}`
  - [ ] `getReviewListApi(params)` → `GET /agent/review`
  - [ ] `reviewRecordApi(recordId, data)` → `PUT /agent/review/{id}`
  - [ ] `sendChatMessageApi(data)` → `POST /agent/chat`（Phase 4 就绪后直接可用）

### 状态管理（`frontend_vue3/src/store/modules/agent.ts`）

- [ ] 创建 Pinia Store，定义以下状态：
  - [ ] `panelVisible: boolean` — 面板开关
  - [ ] `activeTab: 'chat' | 'ingest' | 'review'` — 当前 Tab
  - [ ] `chatMessages: ChatMessage[]` — 对话历史（持久化到 localStorage）
  - [ ] `chatLoading: boolean` — 对话等待状态
  - [ ] `activeTasks: AgentTask[]` — 进行中的摄取任务
  - [ ] `unreadCount: number` — 未读计数（FAB 徽标）

### 任务轮询（`frontend_vue3/src/composables/useAgentTasks.ts`）

- [ ] 基于 `@vueuse/core` 的 `useIntervalFn` 实现轮询。
- [ ] 仅轮询 `pending` / `running` 状态的任务，完成后自动停止。
- [ ] 面板打开间隔 3 秒，面板关闭降频到 10 秒。
- [ ] 任务状态变更时更新 Store 并发送 `ElNotification` 通知。

### 组件开发（`frontend_vue3/src/components/AgentPanel/`）

**index.vue — 主入口**

- [ ] 右下角固定定位 FAB 按钮（`el-button circle`），带 `el-badge` 显示未读计数。
- [ ] 点击打开 `el-drawer`（右侧滑出，宽度 480px）。
- [ ] Drawer 内部使用 `el-tabs` 切换三个功能区。
- [ ] Review Tab 仅在 admin 角色时显示（从 `useUserStore` 读取）。

**AgentChat.vue — 对话界面**

- [ ] 消息列表区：滚动容器，自动滚动到底部。
- [ ] 每条消息使用 `ChatMessage.vue` 渲染（左侧 Agent 头像 / 右侧用户头像）。
- [ ] 底部输入区：`el-input` + 文件附件按钮 + 发送按钮。
- [ ] Chat 后端未就绪时 catch 错误，显示"Agent 对话功能即将上线"占位提示。

**ChatMessage.vue — 消息气泡**

- [ ] 支持 `user` / `agent` / `system` 三种消息角色样式。
- [ ] Agent 消息支持 Markdown 渲染。

**AgentIngest.vue — 文件摄取**

- [ ] `el-upload` 拖拽上传区域（接受 PDF/图片/CSV，限 20MB）。
- [ ] 上传成功后调用 `submitIngestApi`，返回 task 加入 Store 进入轮询。
- [ ] 任务卡片列表展示实时状态（pending/running/succeeded/failed）。
- [ ] running 显示进度动画，succeeded 显示置信度，failed 显示错误信息。

**AgentReview.vue — 审核管理**

- [ ] 复用 `useTable` composable 模式。
- [ ] `el-table` 展示待审核记录（文件名、置信度、提取数据预览、状态）。
- [ ] 操作列：通过 / 拒绝 / 修改 三个按钮。
- [ ] "修改"弹出 `el-dialog` 供人工修正提取数据（textarea 编辑 JSON）。
- [ ] 分页使用现有 `Pagination` 组件。

### 布局集成

- [ ] 修改 `src/layouts/index.vue`，在 `.app-container` 末尾挂载 `<AgentPanel />`。
- [ ] 无需修改路由或侧边栏配置。

### 验收标准

- [ ] FAB 按钮全局可见，点击可打开/关闭 Drawer。
- [ ] 文件上传后自动建立任务并轮询，任务完成/失败有通知提示。
- [ ] 审核页面仅 admin 可见，通过/拒绝/修改操作正常调用后端 API。
- [ ] Chat Tab 在后端未就绪时显示友好占位提示，不报错。
- [ ] 面板状态（开关、Tab、聊天记录）刷新后保持。

---

## 测试策略

- [ ] 单元测试：SQL 安全层，构造恶意 SQL 样本（注入、DDL、全表扫描等），断言全部被拦截。
- [ ] 单元测试：Schema 校验与置信度计算，固定输入断言输出。
- [ ] 集成测试：Mock OpenAI SDK 返回固定响应，验证 Agent 工具选择正确。
- [ ] 集成测试：使用样本 PDF / CSV 验证摄取管线端到端入库结果。
- [ ] 集成测试：固定自然语言问题集，验证生成 SQL 的正确性与安全性。

---

## MVP 验收标准

- [ ] Deepseek API 通过 OpenAI SDK 调通，Agent 空循环正常运行。
- [ ] PDF / 图片 / CSV 经 MinerU + Deepseek 提取后，结构化数据带溯源元数据写入 PostgreSQL。
- [ ] 低置信度记录进入 `pending_review` 状态，可通过审核 API 完成人工确认。
- [ ] Text-to-SQL 仅查询白名单表，SQL 安全层拦截所有危险查询模式。
- [ ] SQL 执行使用 `agent_readonly` 只读角色，超时 10 秒硬切断。
- [ ] LangChain Agent 能根据用户意图自动选择工具（摄取 / 查询），信息不足时主动追问。
- [ ] 所有 Agent 端点纳入 JWT 认证，操作日志可审计。

---

## 外部前置条件

- [ ] 申请 Deepseek API Key，配置到 `.env` 环境变量。
- [ ] 确认 MinerU API 部署方式（云端调用 / 本地部署）及接口文档。
- [ ] 梳理 projects、materials、fillers、test_results 表结构，用于 Schema Grounding。
- [ ] 准备 1-2 份样本 PDF / 图片 / CSV 文件，用于端到端验证。
- [x] 与前端团队确认审核界面的 UI 需求与交互流程。（已在 Phase 5 中规划）
