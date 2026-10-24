from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = (
        "postgresql+psycopg://semiconductor:semiconductor@localhost:5432/semiconductor"
    )
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "semiconductor-graph"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "troubleshooting_knowledge"
    secom_data_dir: str = "data/raw"


@lru_cache
def get_settings() -> Settings:
    return Settings()
