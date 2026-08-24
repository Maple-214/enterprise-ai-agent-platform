# 02 - Development Guide

## 开发环境

推荐 VS Code + Docker Desktop + uv + Node 20 + pnpm 9。Python 版本由项目根目录 `.python-version` 管理。

## 分工

前端：

```text
apps/web
packages/contracts
```

Agent：

```text
services/agent
services/worker
```

基础设施：

```text
infra
```

## API 代码规范

- route 只做 HTTP 相关逻辑
- Pydantic 做输入输出校验
- Service 做业务规则
- Repository/SQLAlchemy 做数据访问
- Agent Runtime 不依赖 FastAPI Request 对象

## TypeScript 规范

- `strict: true`
- React component props 必须显式定义
- API 返回值必须有类型
- 不使用 `any` 作为默认逃生舱
- 对外 payload 使用 Zod 或 generated schema

## Python 规范

- Python 3.12（由 uv 管理）
- uv
- 类型注解优先
- async IO 优先
- 使用 Ruff / Pytest / MyPy 时再接入公司统一工具链

## 测试

后端：

```bash
uv run --directory services/agent pytest -q
```

前端：

```bash
pnpm --dir apps/web test
```

## Code Review

任何涉及以下模块的 PR 必须检查安全影响：

- auth
- tool
- tenant filter
- file upload
- prompt
- model gateway
- workflow
