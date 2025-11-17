from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BountyNotes API"
    api_prefix: str = "/api"
    environment: str = "development"
    database_url: str = "sqlite:///data/bountynotes.db"
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection_name: str = "bountynotes_chunks"
    qdrant_vector_size: int = 1536
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    openai_base_url: str = "https://api.openai.com/v1"
    deepseek_chat_model: str = "deepseek-chat"
    deepseek_metadata_model: str = "deepseek-chat"
    openai_embedding_model: str = "text-embedding-3-small"
    exa_max_characters: int = 20000
    deepseek_api_key: str = ""
    openai_api_key: str = ""
    exa_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
