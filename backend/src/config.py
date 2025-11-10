from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "CheckList API"
    api_version: str = "0.1.0"
    
    # CORS Settings
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "https://*.vercel.app",
    ]
    
    # OpenAI Settings
    openai_api_key: str = "sk-test-key"  # Default for testing
    openai_model: str = "gpt-4-turbo-preview"
    
    # Anthropic Settings
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # Weaviate Settings
    weaviate_url: str = "http://localhost:8080"  # Default for local testing
    weaviate_api_key: str | None = None
    
    # Storage Settings
    storage_type: str = "local"  # local, s3, r2
    local_storage_path: str = "./data"
    s3_bucket: str | None = None
    s3_region: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    
    # Modal Settings
    modal_environment: str = "main"
    modal_token_id: str | None = None
    modal_token_secret: str | None = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()