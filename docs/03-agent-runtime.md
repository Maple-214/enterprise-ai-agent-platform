# 03 - Agent Runtime

## AgentState

Agent State 是 Agent 的唯一上下文来源：

```text
conversation_id
tenant_id
user_id
messages
tool_events
citations
pending_approval
metadata
```

## Graph

```text
START
  ↓
model_node
  ↓
tool_calls?
 ┌───────┴───────┐
 No              Yes
 ↓                ↓
END            tool_node
                  ↓
               model_node
```

## 增加 Specialist

新增：

```text
agents/contract.py
```

然后通过 Supervisor 路由：

```text
Supervisor
 ├── knowledge
 ├── analytics
 └── contract
```

## HITL

高风险 Tool：

```text
requires_approval=true
```

运行状态：

```text
pending_approval
```

前端在 Approval Center 审批后，由 API resume execution。

## 不允许的实现

不要：

```text
API route -> OpenAI SDK -> tool -> DB
```

应该：

```text
API route
  ↓
AgentService
  ↓
Graph
  ↓
ModelGateway / ToolRegistry
```
