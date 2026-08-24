# 04 - RAG & Memory

## RAG

默认数据流：

```text
Upload
 ↓
MinIO
 ↓
Redis Job
 ↓
Worker
 ↓
Parser
 ↓
Chunk
 ↓
Embedding
 ↓
Qdrant
```

当前本地 embedding 是 deterministic hash embedding，目标是保证 Demo 无外网也能跑通。生产切换到真实 embedding 时，保持 `embed()` 接口不变。

## Memory

当前 Memory 分成：

### Short-term

Conversation + Message + Agent Runtime State。

### Long-term

数据库 `memories` 表预留，后续可以接向量检索与 memory summarization。

## Citation

每次 RAG 返回应保留：

```text
source
chunk_id
score
metadata
```

前端必须将 citation 与 answer 绑定展示，而不是只显示“AI 已找到资料”。
