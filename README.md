# Enterprise AI Agent Platform

> 企业级 AI Agent 平台基础工程（Production-oriented Baseline）。
>
> 前端：React + TypeScript + Vite + pnpm  
> Agent 服务：Python 3.12 + FastAPI + LangGraph + uv  
> 基础设施：PostgreSQL + Redis + Qdrant + MinIO  
> 编排方向：Tool Calling / RAG / Memory / Workflow / HITL / Multi-Tenant / RBAC / Evaluation / Observability

这不是一个临时 Demo，而是一套**可以直接启动、可以进入团队协作、可以继续向企业级生产环境演进**的 Agent 平台基线。项目刻意保持简单：前端和 Agent 服务边界清晰，Python 环境统一由 `uv` 管理，基础设施由 Docker Compose 管理。

---

## 1. 你应该如何理解这个项目

```text
                    Browser
                       │
                       ▼
            React + TypeScript + Vite
                       │
                REST / SSE / JSON
                       │
                       ▼
               FastAPI API Layer
                       │
        ┌──────────────┼─────────────────┐
        │              │                 │
        ▼              ▼                 ▼
      Auth          Conversation      Knowledge
      RBAC          Chat / SSE        Upload / RAG
      Tenant
                       │
                       ▼
              LangGraph Agent Runtime
                       │
        ┌──────────────┼─────────────────┐
        ▼              ▼                 ▼
      Tools           RAG              Memory
        │              │                 │
        ▼              ▼                 ▼
       MCP          Qdrant           Checkpoint
                       │
                       ▼
                 Model Gateway
                       │
            ┌──────────┼───────────┐
            ▼          ▼           ▼
          Mock      OpenAI      Compatible
                                   APIs

Infrastructure:
PostgreSQL / Redis / Qdrant / MinIO
Observability:
Prometheus / OpenTelemetry-ready
```

### 当前提供的核心能力

- React + TypeScript 企业控制台
- FastAPI API 服务
- LangGraph Agent Runtime
- Mock LLM，首次运行无需 API Key
- OpenAI-compatible Model Gateway
- Tool Calling
- Calculator / System Status / Knowledge Search Tool
- RAG 文档上传、切块、Embedding、Qdrant 检索
- PostgreSQL 数据模型
- Redis 异步 Worker
- MinIO 文档对象存储
- JWT 登录
- 基础 RBAC / Multi-Tenant 数据隔离
- Approval / Human-in-the-loop 数据模型
- Audit / Evaluation / Workflow 数据模型
- Prometheus `/metrics`
- Alembic 数据库迁移
- 本地开发模式与全 Docker 模式

---

# 2. 仓库目录

```text
enterprise-ai-agent-platform/
│
├── apps/
│   └── web/                         # React + TS + Vite
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── stores/
│       │   ├── lib/
│       │   └── types/
│       ├── Dockerfile
│       ├── nginx.conf
│       ├── package.json
│       └── vite.config.ts
│
├── services/
│   ├── agent/                       # Python Agent/API 服务
│   │   ├── app/
│   │   │   ├── agent/               # LangGraph Runtime / Tools
│   │   │   ├── api/                 # HTTP API
│   │   │   ├── core/                # Config / Security
│   │   │   ├── db/                  # SQLAlchemy Session
│   │   │   ├── models/              # ORM Models
│   │   │   ├── schemas/             # Pydantic Schemas
│   │   │   └── services/            # RAG / Storage / Model / Health
│   │   ├── alembic/                 # 数据库 Migration
│   │   │   └── versions/
│   │   ├── alembic.ini
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   └── worker/                      # Redis Worker
│       ├── worker.py
│       ├── config.py
│       ├── Dockerfile
│       └── pyproject.toml
│
├── infra/
│   ├── keycloak/                    # 后续企业 SSO 接入说明
│   └── prometheus/                  # Metrics 配置
│
├── scripts/
│   ├── dev.ps1                      # Windows 本地开发初始化
│   └── dev.sh                       # macOS/Linux 本地开发初始化
│
├── docs/
│   ├── 01-architecture.md
│   ├── 02-development.md
│   ├── 03-agent-runtime.md
│   ├── 04-rag-memory.md
│   ├── 05-security.md
│   ├── 06-operations.md
│   └── 07-onboarding.md
│
├── .env.example
├── .python-version                  # Python 版本入口
├── docker-compose.yml
├── package.json                     # pnpm workspace root
├── pnpm-workspace.yaml
├── Makefile
└── README.md
```

---

# 3. 技术栈约定

## 前端

- React 19
- TypeScript
- Vite
- React Router
- TanStack Query
- Zustand
- pnpm
- SSE

## Python

- Python 3.12
- **uv**
- FastAPI
- LangGraph
- SQLAlchemy Async
- Alembic
- Pydantic Settings
- Redis asyncio
- Qdrant Client
- boto3 / MinIO
- OpenAI SDK

## 基础设施

- PostgreSQL 16
- Redis 7
- Qdrant
- MinIO
- Docker Compose v2

---

# 4. 环境要求

## Windows / macOS / Linux

必须安装：

```text
Git
Docker Desktop / Docker Engine + Compose v2
Node.js 20+
pnpm 9+
uv
```

检查：

```powershell
git --version
docker --version
docker compose version
node -v
pnpm -v
uv --version
```

Windows 安装 uv 的一种方式：

```powershell
winget install --id=astral-sh.uv -e
```

---

# 5. 第一次启动：推荐本地开发模式

这是日常开发最推荐的方式：

```text
Docker：PostgreSQL / Redis / Qdrant / MinIO
本机：React / FastAPI / Worker
```

## Step 1：进入项目

```powershell
cd \code-project\enterprise-ai-agent-platform
```

## Step 2：创建环境变量

Windows：

```powershell
Copy-Item .env.example .env
```

macOS/Linux：

```bash
cp .env.example .env
```

第一次默认：

```env
LLM_PROVIDER=mock
```

因此**第一次启动不需要模型 API Key**。

---

## Step 3：启动基础设施

```powershell
docker compose up -d postgres redis qdrant minio
```

查看状态：

```powershell
docker compose ps
```

应该看到：

```text
postgres
redis
qdrant
minio
```

---

## Step 4：初始化 Python 环境

Agent：

```powershell
uv sync --directory services/agent
```

Worker：

```powershell
uv sync --directory services/worker
```

> `uv` 会根据 `pyproject.toml` 创建和管理项目环境，不需要手工 `python -m venv`，也不需要手工 activate。

如果仓库中还没有 `uv.lock`，第一次联网开发时执行：

```powershell
uv lock --directory services/agent
uv lock --directory services/worker
```

然后将两个 `uv.lock` 提交 Git。团队后续统一使用：

```powershell
uv sync --directory services/agent --locked
uv sync --directory services/worker --locked
```

---

## Step 5：执行数据库迁移

```powershell
uv run --directory services/agent alembic upgrade head
```

以后数据库结构发生变更，不要再使用 `Base.metadata.create_all()` 直接覆盖生产数据库，而是创建 Alembic migration：

```powershell
uv run --directory services/agent alembic revision --autogenerate -m "describe your change"
uv run --directory services/agent alembic upgrade head
```

---

## Step 6：启动 Agent API

终端 1：

```powershell
uv run --directory services/agent uvicorn app.main:app --reload --port 8000
```

API 文档：

```text
http://localhost:8000/docs
```

存活检查：

```text
http://localhost:8000/health/live
```

就绪检查：

```text
http://localhost:8000/health/ready
```

Metrics：

```text
http://localhost:8000/metrics
```

---

## Step 7：启动 Worker

终端 2：

```powershell
uv run --directory services/worker python worker.py
```

Worker 负责：

```text
Redis job queue
 ↓
文档解析
 ↓
Embedding
 ↓
Qdrant indexing
```

Worker 在 Redis 暂时不可用时会自动重试，不会因为一次连接失败直接退出。

---

## Step 8：启动前端

终端 3：

```powershell
pnpm install
pnpm --dir apps/web dev
```

浏览器：

```text
http://localhost:5173
```

Vite 会把：

```text
/api/*
/health/*
```

代理到：

```text
http://localhost:8000
```

所以本地开发不需要额外处理 CORS 地址。

---

# 6. 一次性初始化脚本

Windows 可以先执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1
```

这个脚本会：

1. 检查 Docker
2. 启动 PostgreSQL / Redis / Qdrant / MinIO
3. 执行 `uv sync`
4. 执行 Alembic migration
5. 输出 API / Worker / Web 启动命令

> 它不会把三个长期运行进程塞在一个终端中，避免 Windows 下调试困难。

---

# 7. 默认开发账号

项目第一次启动 API 后会自动创建 Demo Tenant 和 Demo Agent。

```text
Email:
demo@company.local

Password:
Demo123!
```

生产环境必须关闭：

```env
DEMO_BOOTSTRAP=false
```

并修改：

```env
SECRET_KEY=<strong-random-secret>
```

---

# 8. 真实大模型配置

默认：

```env
LLM_PROVIDER=mock
```

切换到 OpenAI-compatible API：

```env
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=YOUR_API_KEY
LLM_MODEL=YOUR_MODEL
```

只需要改变环境变量，不需要改 Agent Runtime。

因此后续可以接入：

```text
OpenAI
DeepSeek
Qwen
Kimi
企业内部 OpenAI-compatible Gateway
```

---

# 9. 本地开发端口

| 服务 | 地址 |
|---|---|
| Web | `http://localhost:5173` |
| API | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| API Live | `http://localhost:8000/health/live` |
| API Ready | `http://localhost:8000/health/ready` |
| Metrics | `http://localhost:8000/metrics` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |
| Qdrant | `localhost:6333` |
| MinIO API | `localhost:9000` |
| MinIO Console | `http://localhost:9001` |

---

# 10. Docker 全量启动

如果希望整个项目全部容器化：

```powershell
docker compose up -d --build
```

启动后：

```text
Web:
http://localhost:5173

API:
http://localhost:8000/docs
```

容器内部服务发现：

```text
postgres:5432
redis:6379
qdrant:6333
minio:9000
```

Docker 模式下 `docker-compose.yml` 会覆盖这些地址；本机开发则使用 `localhost`。不要把 Docker service name 硬编码到本地 `.env`。

停止：

```powershell
docker compose down
```

停止并删除数据卷（危险）：

```powershell
docker compose down -v
```

---

# 11. Agent 工作机制

当前 Runtime 核心：

```text
User Message
    ↓
LangGraph Model Node
    ↓
模型是否需要 Tool？
 ┌──────────────┐
 │              │
 No             Yes
 │              │
 ▼              ▼
Answer       Tool Node
                ↓
             Tool Result
                ↓
             Model Node
                ↓
              Answer
```

当前基础 Tool：

```text
calculator
get_system_status
knowledge_search
```

以后新增企业工具时，应该统一走 Tool Registry / Policy，而不是在 API Controller 中堆业务逻辑。

---

# 12. RAG 工作机制

```text
Upload
  ↓
MinIO
  ↓
Redis Job
  ↓
Worker
  ↓
PDF / TXT / MD Parsing
  ↓
Chunking
  ↓
Embedding
  ↓
Qdrant
  ↓
Agent Tool
  ↓
Tenant-filtered Retrieval
```

Qdrant payload 中包含：

```text
tenant_id
document_id
filename
chunk_index
text
```

查询时必须使用 `tenant_id` 过滤，避免多租户数据串库。

---

# 13. 数据库维护

数据库结构统一通过 Alembic 管理：

```text
services/agent/alembic/
```

查看当前版本：

```powershell
uv run --directory services/agent alembic current
```

查看历史：

```powershell
uv run --directory services/agent alembic history
```

升级：

```powershell
uv run --directory services/agent alembic upgrade head
```

回退一个版本：

```powershell
uv run --directory services/agent alembic downgrade -1
```

创建 migration：

```powershell
uv run --directory services/agent alembic revision --autogenerate -m "add agent version"
```

注意：自动生成 migration 后必须人工审查，不要直接无脑提交。

---

# 14. uv 团队规范

## 允许

```powershell
uv sync --directory services/agent
uv run --directory services/agent pytest -q
uv add --directory services/agent <package>
uv remove --directory services/agent <package>
uv lock --directory services/agent
```

## 不建议

```powershell
pip install ...
python -m venv .venv
pip freeze > requirements.txt
```

本项目不使用 `requirements.txt` 作为依赖源。

### Python 版本

`.python-version` 是项目 Python 版本入口。

当前：

```text
3.12
```

如果未来升级到 3.13，需要：

1. 修改 `.python-version`
2. 评估 Agent 依赖兼容性
3. 在 CI 中验证
4. 重新生成 `uv.lock`
5. 全量测试
6. 再进入生产环境

---

# 15. 前端依赖规范

前端统一使用 pnpm：

```powershell
pnpm install
pnpm add <package> --filter @enterprise-agent/web
pnpm remove <package> --filter @enterprise-agent/web
```

不要混用 npm / yarn。

构建：

```powershell
pnpm --dir apps/web build
```

类型检查：

```powershell
pnpm --dir apps/web typecheck
```

测试：

```powershell
pnpm --dir apps/web test
```

---

# 16. 测试策略

后续团队扩展建议保持三层测试：

```text
Unit
 ↓
Integration
 ↓
E2E
```

当前已有：

```text
services/agent/tests/
apps/web/
```

Agent 新功能至少应该覆盖：

```text
正常输入
Tool Calling
Tool Error
RAG 无结果
RAG 有结果
Tenant Isolation
权限限制
```

---

# 17. 生产环境基线

当前 `docker compose` 可以作为：

> **单机 / 小规模生产部署基线**

但真正的大规模企业生产环境应继续演进到：

```text
Load Balancer / API Gateway
        ↓
Multiple API replicas
        ↓
Redis HA
PostgreSQL HA
Qdrant Cluster
Object Storage / S3
        ↓
Kubernetes
```

生产环境必须额外处理：

- Secret Manager
- TLS
- WAF / Rate Limit
- SSO / OIDC
- Audit Log
- Centralized Logging
- Metrics / Tracing
- Database Backup
- Disaster Recovery
- Resource Quota
- Model Cost Control
- PII / Data Governance

---

# 18. 发布前检查清单

```text
[ ] .env 中 SECRET_KEY 已更换
[ ] DEMO_BOOTSTRAP=false
[ ] 真实模型 API Key 使用 Secret Manager
[ ] uv.lock 已提交
[ ] pnpm lockfile 已提交
[ ] alembic upgrade head 验证通过
[ ] Unit Test 通过
[ ] Integration Test 通过
[ ] Web Production Build 通过
[ ] /health/ready 正常
[ ] Prometheus metrics 正常
[ ] PostgreSQL 已备份
[ ] Redis 持久化策略已确认
[ ] Qdrant 数据备份策略已确认
[ ] MinIO/S3 数据备份策略已确认
[ ] CORS 已限制到真实域名
[ ] 认证 / RBAC 已验证
[ ] Tenant 数据隔离已验证
[ ] Tool 权限与高风险工具 Approval 已验证
```

---

# 19. 团队 Git 规范

推荐：

```text
feat: add knowledge reranker
fix: handle qdrant timeout
refactor: extract tool registry
chore: upgrade langgraph
perf: optimize retrieval
security: harden tool permissions
```

Feature 开发流程：

```text
issue
 ↓
branch
 ↓
implementation
 ↓
test
 ↓
code review
 ↓
merge
 ↓
CI
 ↓
deploy
```

---

# 20. 新成员 Onboarding

新同学加入后按顺序：

```text
1. 安装 Node / pnpm / uv / Docker
2. clone repository
3. Copy .env.example .env
4. docker compose up -d postgres redis qdrant minio
5. uv sync --directory services/agent
6. uv sync --directory services/worker
7. uv run --directory services/agent alembic upgrade head
8. 启动 API
9. 启动 Worker
10. pnpm install
11. 启动 Web
12. 登录 Demo 账号
13. 运行 Calculator Tool
14. 上传测试文档并验证 RAG
```

建议新成员第一天只阅读：

```text
docs/01-architecture.md
docs/02-development.md
docs/03-agent-runtime.md
docs/04-rag-memory.md
```

---

# 21. 常见问题

## Worker 报 `Error 11001 connecting to redis:6379`

这是本地进程连接 Docker Redis 时使用了 Docker service name。

本地 `.env` 必须：

```env
REDIS_URL=redis://localhost:6379/0
```

Docker Compose 内部才使用：

```text
redis:6379
```

---

## SQLAlchemy 报 `metadata is reserved`

不要把 ORM Python 属性命名为 `metadata`。

正确：

```python
audit_metadata = mapped_column("metadata", JSON)
```

---

## Qdrant / MinIO 尚未 ready

先执行：

```powershell
docker compose ps
docker compose logs qdrant
docker compose logs minio
```

API 启动时自身也会进行依赖重试。

---

## uv 找不到 Python

```powershell
uv python install 3.12
uv python pin 3.12
uv sync --directory services/agent
```

---

# 22. 长期演进路线

当前版本是稳定基线，后续推荐按下面顺序演进：

```text
Phase 1
单 Agent + Tool + RAG

Phase 2
Streaming + Memory + Checkpoint

Phase 3
Workflow + Human Approval

Phase 4
Tool Registry + MCP

Phase 5
Multi-Agent / Supervisor

Phase 6
Evaluation / Dataset / LLM Judge

Phase 7
Observability / Trace / Cost

Phase 8
SSO / RBAC / Tenant Governance

Phase 9
Kubernetes / HA / Autoscaling

Phase 10
Enterprise Data Governance / Security
```

不要为了“架构看起来大”一次性实现全部高级能力。当前仓库已经把模块边界预留好，后续可以增量演进，不需要推翻 Agent Runtime 或前端。

---

# 23. 项目工程原则

1. **前端与 Agent Runtime 解耦**：React 不直接承载 Agent 业务逻辑。
2. **Python 使用 uv**：环境、依赖、版本、锁文件统一管理。
3. **数据库必须迁移**：生产环境不使用 `create_all()` 作为 schema 管理方案。
4. **基础设施地址由环境决定**：本地使用 `localhost`，容器使用 service name。
5. **多租户优先**：业务查询必须带 `tenant_id` 边界。
6. **Tool First-class**：企业能力通过 Tool / MCP 扩展，不直接嵌入 Prompt。
7. **可观测性优先**：所有长任务、Tool、模型调用最终都应该进入 trace。
8. **可测试**：Agent 的行为需要 Dataset 和 Evaluation，而不是只人工点几次。
9. **配置与代码分离**：模型、数据库、Secret、Provider 等通过环境变量控制。
10. **先稳定，再扩展**：保持当前平台边界稳定，再逐步增加 Multi-Agent、Workflow、MCP、Evaluation。

---

# 24. License / Internal Use

当前仓库作为企业内部 Agent 平台基础工程使用。正式对外发布前，请根据实际组织要求补充 License、第三方依赖合规及安全审计说明。
