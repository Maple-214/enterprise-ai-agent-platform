# 对话运行态设计

## 1. 两种状态必须分离

### Conversation 状态

- `active`：对话正常可继续使用。
- `archived`：用户主动归档。

`Conversation.status` 不代表 Agent 是否正在执行。

### Run 状态

- `queued`：任务已创建，等待执行。
- `running`：Agent 正在执行。
- `completed`：执行成功。
- `failed`：执行失败。
- `cancelled`：执行被取消。

前端的“执行中”必须来自 `Run.status in ('queued', 'running')`，不能来自 `Conversation.status === 'active'`。

## 2. Conversation 列表聚合字段

`GET /api/conversations` 对每个会话返回：

- `latest_run`：最近一次 Run 摘要。
- `is_running`：当前是否存在 `queued/running` Run。

`is_running` 是列表 UI 的唯一“执行中”判断依据。

## 3. 并发约束

同一个 Conversation 默认只允许同时存在一个 `queued/running` Run。

数据库通过 PostgreSQL 部分唯一索引兜底：

```sql
CREATE UNIQUE INDEX uq_runs_one_active_per_conversation
ON runs (conversation_id)
WHERE status IN ('queued', 'running');
```

应用层同时返回 HTTP 409，提供更友好的提示。

## 4. 前端切换对话

切换对话不会取消原来的 Run。

例如 A 正在执行，用户切换到 B：

- A 仍然显示“执行中”。
- B 可以正常查看和操作。
- A 完成后，A 的“执行中”自动消失。

当前输入框是否禁用，只取决于当前选中的 Conversation 是否 `is_running === true`。
