from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://support_user:support_pass@localhost:5432/support_platform"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"

    jwt_secret: str = "dev_secret_change_me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    upload_dir: str = "uploads"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
