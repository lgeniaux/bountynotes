from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BountyNotes API"
    api_prefix: str = "/api"
    environment: str = "development"
    database_url: str = "sqlite:///data/bountynotes.db"
    qdrant_url: str | None = None
    qdrant_collection_name: str | None = None
    qdrant_vector_size: int | None = None
    deepseek_base_url: str | None = None
    openai_base_url: str | None = None
    deepseek_chat_model: str | None = None
    deepseek_metadata_model: str | None = None
    openai_embedding_model: str | None = None
    exa_max_characters: int = 20000
    deepseek_api_key: str = ""
    openai_api_key: str = ""
    exa_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
