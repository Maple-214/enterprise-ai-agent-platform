# 基线版本变更记录

## Conversation / Run 领域定型版

本版本正式将会话管理与 Agent 执行解耦：

```text
Conversation
    ↓
Run
    ↓
RunEvent / ToolExecution / Message
    ↓
LangGraph Runtime
```

### 关键变化

1. Conversation 支持创建、列表、搜索、分页、重命名、置顶、归档、恢复、软删除、清空消息。
2. Message 增加 `run_id`，可以追踪消息属于哪一次 Agent 执行。
3. 新增 Run、RunEvent、ToolExecution 数据模型。
4. 新增 `/api/runs/*` API，流式执行入口迁移到 Run 域。
5. 保留 `/api/chat/stream` 作为兼容入口。
6. 前端对话页面改为“先创建/选择对话，再发送任务”。
7. 所有用户可见业务文案统一使用中文。
8. 新增会话与执行任务领域说明文档。
