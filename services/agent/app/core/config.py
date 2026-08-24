from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[4]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "enterprise-ai-agent-platform"
    secret_key: str = "change-this"
    access_token_expire_minutes: int = 720

    database_url: str = "postgresql+asyncpg://agent:agent_password@localhost:5432/agent_platform"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "knowledge_chunks"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "agent-documents"
    minio_secure: bool = False

    llm_provider: str = "mock"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    web_origin: str = "http://localhost:5173"
    demo_bootstrap: bool = True
    demo_email: str = "demo@company.local"
    demo_password: str = "Demo123!"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
