# 05 - Security

## 身份

开发：JWT。

企业：OIDC / SSO。

## 授权

建议从 Role 逐步升级为 Permission：

```text
agent.read
agent.write
agent.publish
knowledge.read
knowledge.write
approval.read
approval.approve
audit.read
```

## Multi Tenant

任何查询都必须有 Tenant Scope。

## Tool Security

Tool 至少包含：

```text
risk_level
requires_approval
allowed_roles
rate_limit
idempotency_key
```

## 文件安全

生产必须增加：

- 文件大小限制
- MIME 校验
- 恶意文件扫描
- 解压炸弹防护
- OCR/Parser 沙箱
- MinIO 私有 Bucket

## Prompt Injection

不要把检索到的文本直接视为系统指令。把所有外部内容视为 untrusted data。

Tool schema 必须白名单控制，不能允许模型动态生成任意函数名或任意网络请求。
