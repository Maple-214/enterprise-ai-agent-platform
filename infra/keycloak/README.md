# Keycloak（可选）

项目默认不强制依赖 Keycloak，因为这样可以保证 Docker Compose 一键启动速度更快。

企业环境接入 OIDC 时：

1. 启动 Keycloak
2. 创建 Realm / Client
3. 前端拿 OIDC Token
4. FastAPI 校验 JWT issuer / audience
5. 将 claims 映射为 tenant / role / permission

当前 JWT 登录是开发基线，生产应逐步切换到公司统一 SSO。
