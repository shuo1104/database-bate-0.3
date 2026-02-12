# Agent 系统实施计划

本文档记录 Agent 系统的技术选型、目录结构与分阶段构建计划。
Agent 属于后端能力，代码位于 `backend_fastapi/app/agent`，文档紧邻代码放置。

---

## 基础约定

- **运行环境**：统一使用 **conda 的 `database` 虚拟环境** 进行开发、测试与部署运维。所有 `pip install`、脚本执行、服务启动均在该环境下进行。
- **可移植性原则**：一切配置与部署操作遵守 **"更换生产服务器环境后能快速移植部署"** 的原则。具体要求：
  - 敏感信息（API Key、数据库密码等）一律通过 `.env` 环境变量注入，不硬编码在源码中。
  - 路径使用相对路径或配置项，不写死本机绝对路径。
  - 依赖版本锁定在 `requirements.txt`，确保 `conda activate database && pip install -r requirements.txt` 即可复现环境。
  - 数据库变更通过 Alembic 迁移管理，不依赖手动 DDL。

---

## 一、技术选型

| 能力 | 方案 | 说明 |
|------|------|------|
| LLM 调用 | **Deepseek**（通过 OpenAI SDK 兼容接口） | 使用 `openai` Python 包，`base_url` 指向 Deepseek API |
| OCR / 文档解析 | **MinerU API** | 支持 PDF、图片等文档的结构化提取 |
| Agent 框架 | **LangChain** | 提供 ReAct Agent、Tool 注册、Memory、Chain 等开箱即用能力 |
| ML 推理 | **现有模型**（预留集成接口） | 模型已独立存在，Agent 仅需调用接口，目录保留为占位 |
| 数据库 | **PostgreSQL**（沿用现有） | 异步驱动 asyncpg，ORM 使用 SQLAlchemy 2.0 |
| 异步任务 | **FastAPI BackgroundTasks** + 状态轮询 | 长耗时操作（OCR、LLM）放入后台，前端通过轮询获取结果。MVP 阶段适用；生产环境如需持久化和重试机制，后续考虑迁移至 Celery + Redis |

### 新增依赖（需追加到 requirements.txt）

```
langchain>=0.2
langchain-openai>=0.1
openai>=1.0
```

MinerU 如果以 HTTP API 方式调用，则无需额外包；如果本地部署则按其文档添加依赖。

---

## 二、目录结构

仅定义文件夹层级，具体文件在各阶段实现时按需创建。每个目录含 `__init__.py` 以构成 Python 包。

```
backend_fastapi/app/agent/
│
├── doc/                    # 设计文档与决策记录
│
├── config/                 # 策略配置（引用 app/config/settings.py 全局实例）
│                           #   - Deepseek LLM 参数
│                           #   - SQL 安全策略
│                           #   - MinerU API 参数
│
├── core/                   # LangChain Agent 编排核心
│                           #   - Agent 初始化与运行入口
│                           #   - Tool 注册表
│                           #   - Memory / 会话状态管理
│                           #   - 回调与日志钩子
│
├── tools/                  # Agent 可调用的工具集
│   ├── etl/                #   文档解析与数据入库工具
│   │                       #     - MinerU OCR 调用
│   │                       #     - LLM 辅助结构化提取（Deepseek）
│   │                       #     - 字段校验与置信度评分
│   │                       #     - PostgreSQL 入库
│   │
│   ├── sql/                #   Text-to-SQL 查询工具
│   │                       #     - Schema Grounding（表结构注入 Prompt）
│   │                       #     - SQL 安全层（白名单、形状检查、超时）
│   │                       #     - 执行与自纠错循环
│   │
│   └── ml/                 #   ML 推理工具（占位，待集成）
│                           #     - 预留调用接口，模型已独立存在
│
├── schemas/                # Pydantic 数据模型（请求/响应/中间结构）
│
├── api/                    # Agent 对外 API 端点
│                           #   - 注册到 app/api/v1 路由体系
│                           #   - 支持同步响应与异步任务两种模式
│
└── tests/                  # 测试
                            #   - LLM Mock 单元测试
                            #   - SQL 安全层测试
                            #   - 端到端集成测试
```

---

## 三、系统能力范围

| 能力 | 说明 | 状态 |
|------|------|------|
| 文档摄取 | PDF / 图片 / CSV → MinerU 解析 → Deepseek 结构化提取 → 校验 → 入库 PostgreSQL | 计划中 |
| 结构化查询 | 自然语言 → Text-to-SQL → 安全校验 → 执行 → 格式化返回 | 计划中 |
| ML 预测 | 调用现有模型接口，返回推荐结果与置信度 | 占位预留 |
| Agent 编排 | LangChain ReAct Agent 自动选择工具、处理多步任务、主动追问缺失信息 | 计划中 |

> RAG（检索增强生成）当前不纳入范围。如后续需要文档语义检索，可在 `tools/` 下新增 `rag/` 目录，基于 pgvector 扩展实现。

---

## 四、分阶段构建计划

> **设计原则**：每个 Phase 可独立交付验证，不存在对后续 Phase 的前置依赖。

### Phase 0 — 基线搭建与 Agent 骨架

**目标**：完成技术栈接入验证，搭建最小可运行的 LangChain Agent，准备好数据库表和配置体系。

1. **依赖与包结构**：安装依赖（langchain、langchain-openai、openai），创建 `agent/` 及所有子目录的完整 Python 包结构（含 `__init__.py`）。
2. **配置集成**：在 `app/config/settings.py` 中新增 Agent 相关配置字段（`DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`MINERU_API_URL`、`AGENT_SQL_TIMEOUT`、`AGENT_SQL_ALLOWLIST_TABLES` 等），更新 `env/env.example` 模板。`agent/config/` 下的策略配置引用 `settings` 全局实例，不另建独立配置文件入口。
3. **数据库准备**：定义 Agent 所需的 ORM 模型（`AgentTask` 异步任务跟踪、`AgentIngestRecord` 摄取记录、`AgentAuditLog` 审计日志），生成 Alembic 迁移并执行。同时创建 PostgreSQL 只读角色 `agent_readonly`，仅授予 SELECT 权限于白名单表，在 `scripts/` 下保留初始化 SQL 脚本。
4. **Agent 骨架**：验证 Deepseek API 连通性。在 `agent/core/` 中初始化 LangChain Agent（ReAct 模式），暂不注册任何业务 Tool，仅验证 Agent 循环可正常运行。
5. **Schema 定义**：在 `agent/schemas/` 中定义摄取输出和查询请求的 Pydantic 基础模型。
6. **测试基础**：建立 `agent/tests/` 基础测试框架，包含 LLM Mock 辅助工具。

**关键产出**：
- Agent 能通过 Deepseek 完成一次空对话循环
- 配置体系就绪，环境变量模板已更新
- 数据库表和只读角色就绪
- Schema 基础模型就绪

---

### Phase 1 — 文档摄取（MinerU + ETL）

**目标**：实现从文件上传到结构化数据入库的完整管线，并提供可独立验证的 API 端点。

1. **API 端点**：在 `app/api/v1/modules/` 下创建 `agent` 模块，遵循项目已有的 Controller → Service 分层模式，注册到 `api_router`。本阶段实现以下端点：
   - `POST /api/v1/agent/ingest` — 提交文件摄取任务，立即返回任务 ID。
   - `GET /api/v1/agent/tasks/{id}` — 查询异步任务状态与结果。
   - `GET /api/v1/agent/review` — 获取待人工审核的摄取记录列表。
   - `PUT /api/v1/agent/review/{id}` — 提交审核结果（通过 / 拒绝 / 修改字段值）。
2. **文件接收**：支持 PDF、图片、CSV 上传，存储原始文件并写入 `AgentTask` 记录。
3. **文档解析**：调用 MinerU API 进行 OCR / PDF 解析，获取原始文本或半结构化内容。
4. **结构化提取**：将 MinerU 输出送入 Deepseek，通过 Prompt 提取为目标 JSON Schema（配方字段、原料参数等）。
5. **校验与置信度**：对提取字段做类型检查、范围校验，为每个字段标记置信度分数。
6. **低置信度处理**：置信度低于阈值的记录标记为 `pending_review` 状态写入 `AgentIngestRecord`，等待人工确认。后端提供审核 API（步骤 1 已实现），前端团队独立开发审核界面来调用这些 API。
7. **入库**：通过现有 SQLAlchemy 异步会话将校验通过的数据写入 PostgreSQL，记录溯源信息（原始文件路径、提取时间、置信度）。
8. **注册 LangChain Tool**：将摄取能力封装为 LangChain Tool，注册到 Agent。

**异步处理**：OCR + LLM 提取耗时较长（数秒至数十秒），采用 FastAPI BackgroundTasks 异步执行。`POST /api/v1/agent/ingest` 立即返回任务 ID，前端通过 `GET /api/v1/agent/tasks/{id}` 轮询结果。

---

### Phase 2 — 结构化查询（Text-to-SQL）

**目标**：用户用自然语言查询数据库，Agent 自动生成安全 SQL 并返回结果。

1. **Schema Grounding**：将目标表的结构信息（表名、字段名、字段类型、示例值）注入到 Prompt 上下文中，引导 Deepseek 生成准确 SQL。目标表范围：projects、materials、fillers、test_results 及其关联关系。
2. **SQL 安全层**：
   - 白名单：仅允许查询指定表，禁止 DDL 和 DML（INSERT/UPDATE/DELETE）。
   - 形状检查：拒绝包含子查询嵌套超过 2 层、UNION 超过 3 条、无 WHERE 的全表扫描等危险模式。
   - 超时：查询执行硬超时 10 秒，超时即终止。
   - 数据权限：SQL 执行使用 `agent_readonly` 只读角色，从数据库层面杜绝写操作。
3. **自纠错循环**：SQL 执行失败时，将错误信息反馈给 Deepseek 重新生成，最多重试 2 次。
4. **结果格式化**：将查询结果格式化为用户友好的文本或表格形式返回。
5. **注册 LangChain Tool**：将 Text-to-SQL 能力封装为 LangChain Tool。

---

### Phase 3 — ML 推理集成（占位预留）

**目标**：预留 ML 推理工具的集成接口，当前不实现具体逻辑。

1. 在 `agent/tools/ml/` 下建立目录结构。
2. 定义 ML 工具的输入输出 Schema（特征字段、预测结果、置信度）。
3. 预留 LangChain Tool 注册入口，待模型接口就绪后接入。

> 后续集成时，Agent 需要判断所需特征是否完整。如不完整，通过 LangChain Agent 的 ReAct 机制主动向用户追问或从数据库补全。

---

### Phase 4 — Chat 端点与生产加固

**目标**：实现核心对话端点，完善认证、审计、错误处理等生产环境所需的周边能力。

> 摄取、任务查询、审核端点已在 Phase 1 中创建。本阶段聚焦 Chat 端点和全局加固。

1. **Chat 端点**：实现 `POST /api/v1/agent/chat` — 发送用户查询（文本 + 可选文件），Agent 根据意图自动选择工具（摄取 / 查询），信息不足时主动追问，返回结构化响应。
2. **认证与权限**：所有 Agent 端点纳入现有 JWT 认证体系。在 `agent/config/` 中定义哪些角色可使用 Agent、哪些角色可审核数据。SQL 查询结果遵循用户数据权限（通过 SQL WHERE 条件注入当前用户的项目范围）。
3. **日志与审计**：通过 LangChain Callback 机制记录每次 Agent 调用的完整链路（用户输入、工具选择、工具参数、工具输出、最终响应、耗时），写入 `AgentAuditLog` 表。关键操作（数据入库、审核通过）同步记录供审计。
4. **错误处理与降级**：Deepseek API 超时/不可用时返回友好错误提示；MinerU API 异常时标记任务为 `failed` 并支持重试；SQL 执行异常已在 Phase 2 自纠错循环中覆盖。
5. **应用启动集成**：如 Agent 有初始化逻辑（如预加载 Schema Grounding 数据），接入 `plugin/init_app.py` 的应用生命周期。确认 Agent 端点的认证白名单配置（通常所有端点均需鉴权，不加入 `TOKEN_REQUEST_PATH_EXCLUDE`）。

---

### Phase 5 — 前端 Agent 浮动面板

**目标**：在 Vue 3 前端中以全局浮动面板形式接入 Agent 系统，涵盖对话、文件摄取、审核管理三大功能。

**交互模式**：不新增侧边栏菜单项和路由页面。右下角 FAB 按钮 + 右侧 `el-drawer` 面板，挂载在 `src/layouts/index.vue`，全局可用。

**新增文件**（均在 `frontend_vue3/src/` 下）：

```
api/agent.ts                         # Agent API 封装 + TS 类型定义
store/modules/agent.ts               # Pinia Store（面板状态、聊天记录、任务列表）
composables/useAgentTasks.ts         # 任务轮询（基于 @vueuse/core useIntervalFn）
components/AgentPanel/
  ├── index.vue                      # 主入口：FAB + el-drawer + el-tabs
  ├── AgentChat.vue                  # 对话界面：消息列表 + 输入框 + 文件附件
  ├── ChatMessage.vue                # 单条消息气泡（user / agent / system）
  ├── AgentIngest.vue                # 文件摄取：拖拽上传 + 任务状态卡片
  └── AgentReview.vue                # 审核管理：el-table + 审核操作 Dialog
```

**仅修改一个现有文件**：`src/layouts/index.vue` — 在模板末尾挂载 `<AgentPanel />`。

1. **API 层**：遵循现有 `request<T>()` + TypeScript 接口模式，定义 5 个 API 函数对接后端 `ingest`、`tasks/{id}`、`review`、`review/{id}`、`chat` 端点。
2. **状态管理**：Pinia Store 持久化存储面板开关、当前 Tab、聊天记录、活跃任务列表、未读计数（FAB 徽标）。
3. **任务轮询**：仅对 `pending` / `running` 任务轮询（间隔 3 秒），面板关闭降频到 10 秒。任务完成时 `ElNotification` 通知用户。
4. **对话界面**：消息气泡列表 + 底部输入框 + 文件附件。Chat 后端（Phase 4）未就绪时 catch 错误并显示友好占位提示，后端上线后前端零改动。
5. **文件摄取**：`el-upload` 拖拽上传（PDF/图片/CSV，限 20MB），上传后自动建任务并进入轮询，下方卡片展示各任务实时状态。
6. **审核管理**：复用 `useTable` composable，`el-table` 展示待审核记录，操作列提供通过/拒绝/修改。"修改"弹出 Dialog 编辑提取数据。仅 admin 角色可见此 Tab。

---

## 五、测试策略

| 层级 | 范围 | 方法 |
|------|------|------|
| 单元测试 | SQL 安全层规则校验 | 构造恶意 SQL 样本（注入、DDL、全表扫描等），断言全部被拦截 |
| 单元测试 | Schema 校验与置信度计算 | 固定输入，断言输出字段与分数 |
| 集成测试 | LLM 调用链路 | Mock OpenAI SDK 返回固定响应，验证 Agent 工具选择正确 |
| 集成测试 | 摄取管线 | 使用样本 PDF/CSV，验证端到端入库结果 |
| 集成测试 | Text-to-SQL | 固定自然语言问题集，验证生成 SQL 的正确性与安全性 |

> LLM 输出具有不确定性。集成测试中使用 Mock 保证确定性；定期在真实 API 上运行评估集衡量质量。

---

## 六、验收标准（MVP）

- [ ] Deepseek API 通过 OpenAI SDK 调通，Agent 空循环正常运行。
- [ ] PDF / 图片 / CSV 经 MinerU + Deepseek 提取后，结构化数据带溯源元数据写入 PostgreSQL。
- [ ] 低置信度记录进入 `pending_review` 状态，可通过审核 API 完成人工确认。
- [ ] Text-to-SQL 仅查询白名单表，SQL 安全层拦截所有危险查询模式。
- [ ] SQL 执行使用 `agent_readonly` 只读角色，超时 10 秒硬切断。
- [ ] LangChain Agent 能根据用户意图自动选择工具（摄取 / 查询），信息不足时主动追问。
- [ ] 所有 Agent 端点纳入 JWT 认证，操作日志可审计。

---

## 七、后续待办

1. 申请 Deepseek API Key，配置到 `.env` 环境变量。
2. 确认 MinerU API 部署方式（云端调用 / 本地部署）及接口文档。
3. 梳理 projects、materials、fillers、test_results 表结构，用于 Schema Grounding。
4. 准备 1-2 份样本 PDF / 图片 / CSV 文件，用于 Phase 1 的端到端验证。
5. ~~与前端团队确认审核界面的 UI 需求与交互流程。~~ → 已在 Phase 5 中规划完成。
