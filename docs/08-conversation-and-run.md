# 会话、消息与执行任务模型

这是本项目后续开发必须遵守的核心领域边界。

## 一、Conversation 只负责会话管理

Conversation 表示用户看到的“一个对话”，负责：

- 创建、列表、详情
- 搜索与分页
- 重命名
- 置顶
- 归档与恢复
- 软删除
- 清空消息

它不负责执行 Agent。

## 二、Run 表示一次 Agent 执行

一次用户输入对应一个 Run。一个 Conversation 可以拥有多个 Run：

```text
Conversation
├── Run 001
├── Run 002
└── Run 003
```

Run 负责：

- 生命周期：queued / running / completed / failed / cancelled
- trace_id
- 输入内容
- 使用的 Agent / 模型
- 开始结束时间
- 错误信息

## 三、RunEvent 是可观察的执行事件

例如：

```text
run.created
run.started
tool.started
tool.completed
citation.created
message.created
run.completed
run.failed
run.cancelled
```

后续 Trace、审计、评测、回放能力都应该围绕 Run 和 RunEvent 建设。

## 四、Message 是对话历史

Message 关联 conversation_id，并可关联 run_id：

```text
用户消息 → conversation_id + run_id
助手消息 → conversation_id + run_id
工具消息 → conversation_id + run_id
```

不要把 Agent 运行状态直接塞进 Conversation。

## 五、扩展原则

后续增加 Memory、RAG、Workflow、MCP、Multi-Agent、Human-in-the-loop 时：

```text
Conversation
    ↓
Run
    ↓
Runtime Context
    ├── 对话历史
    ├── 长期记忆
    ├── RAG 检索
    ├── Agent 状态
    ├── Tool
    └── Workflow
```

这样不会破坏 Conversation 业务域。
