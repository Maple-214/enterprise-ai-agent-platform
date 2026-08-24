# 01 - Architecture

## 目标

项目采用前后端解耦架构：

```text
React SPA
   ↓
FastAPI
   ↓
Application Services
   ↓
LangGraph Runtime
   ↓
Tools / RAG / Memory / Model Gateway
```

## 为什么前端使用 React + Vite

这是一个登录后的企业工作台，不以 SEO、SSR 为核心目标。React + Vite 可以把开发重点集中到：

- Agent streaming UI
- Workflow Editor
- Knowledge Management
- Evaluation Dashboard
- Trace Timeline

## 为什么 Agent 使用 Python

AI Agent 的生态和 LangGraph Python 能力更成熟，特别适合快速接入 RAG、模型、Evaluation、Data/Tool SDK。前端只依赖稳定的 API Contract，不依赖 Agent 实现语言。

## 分层原则

```text
API Layer
  ↓
Service Layer
  ↓
Agent Runtime
  ↓
Infrastructure Adapters
```

任何外部服务必须经过 adapter：

```text
ModelGateway
StorageService
VectorService
QueueService
```

避免把第三方 SDK 散落在业务代码里。
