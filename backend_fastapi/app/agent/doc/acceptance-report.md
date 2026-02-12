# Agent 系统各阶段验收报告

本文档汇总 Phase 0 ~ Phase 4 的验收结果、发现的缺陷及修复情况。

---

## Phase 0 — 基线搭建与 Agent 骨架

### 验收结果

| 验收项 | 状态 |
|--------|------|
| `requirements.txt` 新增 langchain/langchain-openai/openai/langgraph 依赖 | 通过 |
| `agent/` 完整包目录结构，每个目录含 `__init__.py` | 通过 |
| `settings.py` 新增 Agent 配置字段（Deepseek/MinerU/SQL） | 通过 |
| `env.example` 补充 Agent 变量模板 | 通过 |
| Agent ReAct 骨架（`react_agent.py`）可执行空循环 | 通过 |
| Deepseek 连通性检查（`llm.py`） | 通过 |
| ORM 模型（AgentTask/AgentIngestRecord/AgentAuditLog） | 通过 |
| Alembic 迁移脚本 | 通过 |
| PostgreSQL `agent_readonly` 只读角色 SQL 脚本 | 通过 |
| Phase 0 测试（`test_phase0_bootstrap.py` + `mock_llm.py`） | 通过 |

### 发现的缺陷与修复

| # | 严重程度 | 描述 | 修复 |
|---|----------|------|------|
| 1 | 严重 | `ChatOpenAI` 的 `api_key` 参数传入 lambda 而非 str | 改为 `api_key=cfg.api_key` |
| 2 | 严重 | `max_tokens` 放在 `model_kwargs` 中而非直接参数 | 改为 `max_tokens=cfg.max_tokens` |
| 3 | 严重 | `settings.py` 的 Agent 字段未使用 `os.getenv()` 加载 | 全部改为 `os.getenv()` 模式 |
| 4 | 严重 | `MINERU_API_URL` 默认值是 API Key 而非 URL | 默认值改为 `http://localhost:8001`，新增 `MINERU_API_KEY` |
| 5 | 严重 | `requirements.txt` 缺少 `langgraph` | 新增 `langgraph>=0.2` |
| 6 | 中等 | `.env` / `.env.dev` 缺少 Agent 配置变量 | 补充全部 Agent 变量 |

---

## Phase 1 — 文档摄取管线

### 验收结果

| 验收项 | 状态 |
|--------|------|
| `POST /api/v1/agent/ingest` 文件上传 + 异步任务创建 | 通过 |
| `GET /api/v1/agent/tasks/{id}` 任务状态查询 | 通过 |
| `GET /api/v1/agent/review` 审核记录分页列表 | 通过 |
| `PUT /api/v1/agent/review/{id}` 审核操作（通过/拒绝/修改） | 通过 |
| MinerU API 调用（OCR/PDF 解析） | 通过 |
| Deepseek 结构化提取 | 通过 |
| 置信度校验与 `pending_review` 低置信度处理 | 通过 |
| 异步管线（BackgroundTasks） | 通过 |
| LangChain Tool 注册（`agent_document_ingest`） | 通过 |
| Phase 1 测试（controller + service） | 通过 |

### 发现的缺陷与修复

| # | 严重程度 | 描述 | 修复 |
|---|----------|------|------|
| 1 | 严重 | `react_agent.py` 的 `api_key` 再次回退为 lambda | 改回 `api_key=cfg.api_key` |
| 2 | 低 | `max_tokens` 回退到 `model_kwargs` | 改回直接参数 |

> 备注：缺陷 1、2 为 Phase 0 修复后的回退，在后续 Phase 中持续出现，最终在 Phase 3 修复时加上了防回退注释。

---

## Phase 2 — 结构化查询（Text-to-SQL）

### 验收结果

| 验收项 | 状态 |
|--------|------|
| Schema Grounding（8 表结构 + 关系 + 示例值注入 Prompt） | 通过 |
| SQL 安全层 — 白名单表校验 | 通过 |
| SQL 安全层 — DDL/DML 关键词拦截 | 通过 |
| SQL 安全层 — 子查询嵌套 > 2 层拦截 | 通过 |
| SQL 安全层 — UNION > 3 条拦截 | 通过 |
| SQL 安全层 — 无 WHERE 全表扫描拦截 | 通过 |
| SQL 执行硬超时（`asyncio.wait_for`） | 通过 |
| `agent_readonly` 只读角色独立连接 | 通过 |
| 自纠错循环（失败后反馈错误给 LLM，最多重试 2 次） | 通过 |
| 结果格式化（Markdown 表格，截断 20 行） | 通过 |
| LangChain Tool 注册（`agent_text_to_sql`） | 通过 |
| 验证样例文档（`phase2-query-samples.md`） | 通过 |
| 测试覆盖（sql_guard 6 用例 + service 3 用例） | 通过 |

### 发现的缺陷与修复

| # | 严重程度 | 描述 | 修复 |
|---|----------|------|------|
| 1 | 严重 | `init_agent_readonly_role.sql` 缺少 `tbl_FormulaComposition` 的 GRANT SELECT | GRANT SELECT 列表补充该表 |
| 2 | 中等 | `settings.py` 的 `AGENT_SQL_ALLOWLIST_TABLES` 未使用 `os.getenv()` | 改为 `json.loads(os.getenv(..., "[]")) or [默认列表]` |
| 3 | 中等 | Schema Grounding `TABLE_COLUMN_HINTS` 与 ORM 模型相比缺失 24 个字段 | 8 张表全部补齐为与 ORM 一致的完整字段 |
| 4 | 低 | `react_agent.py` 的 `max_tokens` 又回退到 `model_kwargs` | 改回直接参数 |
| 5 | 低 | 缺少 schema_grounding / prompting / executor 的单元测试 | 新增 3 个测试文件共 30 个用例 |

---

## Phase 3 — ML 推理集成（占位预留）

### 验收结果

| 验收项 | 状态 |
|--------|------|
| `agent/tools/ml/` 目录结构（`__init__.py` + `predict_tool.py`） | 通过 |
| ML Schema（`MLFeatureSchema` / `MLPredictionInputSchema` / `MLPredictionOutputSchema`） | 通过 |
| LangChain Tool 注册入口（`agent_ml_predict_placeholder`，返回 `not_implemented`） | 通过 |
| `get_registered_agent_tools(include_ml_tool=True)` 按需加载 | 通过 |
| `build_react_agent(include_ml_tool=True)` 参数化控制 | 通过 |

### 发现的缺陷与修复

| # | 严重程度 | 描述 | 修复 |
|---|----------|------|------|
| 1 | 严重 | `react_agent.py` 的 `api_key` 第三次回退为 lambda | 改回 `api_key=cfg.api_key`，加防回退注释 |
| 2 | 低 | 缺少 Phase 3 测试 | 新增 `test_phase3_ml_placeholder.py`（15 个用例） |

---

## Phase 4 — Chat 端点与生产加固

### 验收结果

**Chat 端点**

| 验收项 | 状态 |
|--------|------|
| `POST /api/v1/agent/chat` 实现（message + 可选 file + project_scope + top_k） | 通过 |
| 意图识别（`_infer_intent`：ingest / query / general）与自动工具路由 | 通过 |
| 信息不足时主动追问（project_scope 缺失→ follow_up） | 通过 |
| ReAct Agent 执行 + callback 审计 | 通过 |
| ReAct 失败→ 直接 SQL 降级 / 直接 LLM 降级 | 通过 |

**认证与权限**

| 验收项 | 状态 |
|--------|------|
| 全部 5 个端点使用 JWT 认证（`Depends(get_current_user_info)`） | 通过 |
| `TOKEN_REQUEST_PATH_EXCLUDE` 不含 Agent 路径，启动时校验 | 通过 |
| `config/authorization.py` 定义角色权限（allowed_roles / review_roles / enforce_scope_roles） | 通过 |
| `settings.py` 角色配置走 `json.loads(os.getenv(...))` | 通过 |

**日志与审计**

| 验收项 | 状态 |
|--------|------|
| `AgentAuditCallbackHandler`（LangChain Callback）记录工具链路 | 通过 |
| Chat 6 种场景均写入 `AgentAuditLog`（完成/降级/追问/摄取提交/失败/验证错误） | 通过 |
| Ingest 完成/失败、Review 操作也记录审计 | 通过 |

**错误处理与降级**

| 验收项 | 状态 |
|--------|------|
| Deepseek 不可用→ `degraded=True, retryable=True` | 通过 |
| MinerU 异常→ 任务标记 `failed` + 审计日志 | 通过 |
| LLM Key 缺失→ 友好文本提示 | 通过 |
| ReAct 异常→ 降级到直接 SQL / 直接 LLM | 通过 |

**应用启动集成**

| 验收项 | 状态 |
|--------|------|
| `init_app.py` 中 Schema Grounding 预加载（`AGENT_SCHEMA_GROUNDING_PRELOAD`） | 通过 |
| Agent 路由注册到 `api_router`（前缀 `/agent`） | 通过 |

**测试**

| 验收项 | 状态 |
|--------|------|
| `test_phase4_chat_service.py`（3 用例：scope 追问、ingest 提交、外部服务降级） | 通过 |
| `test_phase4_authorization_config.py`（1 用例：角色策略解析） | 通过 |

### 发现的缺陷与修复

| # | 严重程度 | 描述 | 修复 |
|---|----------|------|------|
| 1 | 中等 | `.env.dev` 缺少 Phase 4 配置变量（角色、预加载、只读连接） | 补充全部变量 |
| 2 | 低 | `AgentAuditCallbackHandler` 无独立测试 | 新增 `test_phase4_audit_callback.py`（10 个用例） |

### 设计备注

**project_scope 数据权限**：当前通过 Prompt 引导 LLM 生成含 `WHERE ProjectID IN (...)` 的 SQL，而非在执行层强制注入。缓解措施：`agent_readonly` 只读角色阻止写操作、user 缺 scope 时返回追问而非执行、全链路审计。如需更强隔离，可在 `SqlReadonlyExecutor` 层面强制追加 WHERE 条件。

---

## 缺陷修复总览

### 按严重程度统计

| 严重程度 | 发现总数 | 已修复 |
|----------|----------|--------|
| 严重 | 9 | 9 |
| 中等 | 5 | 5 |
| 低 | 6 | 6 |
| **合计** | **20** | **20** |

### 反复出现的问题

`react_agent.py` 中 `ChatOpenAI` 的 `api_key` 参数在 Phase 0 → Phase 1 → Phase 3 共回退 3 次。最终修复时加入防回退注释：

```python
# IMPORTANT: api_key must be str, NOT lambda. Do not revert to lambda.
api_key=cfg.api_key,
```

### 新增测试文件汇总

| 文件 | Phase | 用例数 |
|------|-------|--------|
| `test_phase0_bootstrap.py` | 0 | 4 |
| `test_phase1_agent_controller.py` | 1 | 6 |
| `test_phase1_ingest_service.py` | 1 | 5 |
| `test_phase2_sql_guard.py` | 2 | 6 |
| `test_phase2_text_to_sql_service.py` | 2 | 3 |
| `test_phase2_schema_grounding.py` | 2 | 10 |
| `test_phase2_prompting.py` | 2 | 8 |
| `test_phase2_executor.py` | 2 | 12 |
| `test_phase3_ml_placeholder.py` | 3 | 15 |
| `test_phase4_chat_service.py` | 4 | 3 |
| `test_phase4_authorization_config.py` | 4 | 1 |
| `test_phase4_audit_callback.py` | 4 | 10 |
| **合计** | — | **83** |
