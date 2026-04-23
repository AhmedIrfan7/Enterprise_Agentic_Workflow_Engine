from typing import List, Literal
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Enterprise Agentic Workflow Engine"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # LLM
    LLM_PROVIDER: Literal["openai", "ollama"] = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = Field(default=0.2, ge=0.0, le=2.0)
    LLM_MAX_TOKENS: int = Field(default=4096, ge=1)
    OPENAI_API_KEY: str = ""

    # Local LLM (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./enterprise_workflows.db"

    # Vector store
    VECTOR_STORE_TYPE: Literal["faiss", "chroma"] = "faiss"
    VECTOR_STORE_PATH: str = "./faiss_index"
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # File uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
