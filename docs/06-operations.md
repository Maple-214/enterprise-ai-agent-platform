# 06 - Operations

## 开发

```bash
docker compose up -d --build
```

## 停止

```bash
docker compose down
```

## 清空本地数据

```bash
docker compose down -v
```

## 日志

```bash
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f web
```

## 数据备份

生产必须至少：

- PostgreSQL PITR
- Object Storage versioning
- Qdrant snapshot
- Redis 不作为唯一事实来源

## 发布

建议：

```text
PR
 ↓
CI
 ├── TS typecheck
 ├── frontend build
 ├── backend test
 ├── security scan
 └── image build
 ↓
staging
 ↓
evaluation
 ↓
canary
 ↓
production
```

## 监控

必须监控：

- API p95
- Agent run duration
- Tool error rate
- LLM error rate
- Queue depth
- Worker lag
- Token usage
- estimated cost
- DB connection pool
- Qdrant health
