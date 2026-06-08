from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    app_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://md_converter:md_converter@localhost:5432/md_converter"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket_uploads: str = "uploads"
    s3_bucket_outputs: str = "outputs"
    signed_url_ttl_seconds: int = 3600
    max_upload_size_bytes: int = 524_288_000
    max_pdf_pages: int = 1000
    max_pptx_slides: int = 500
    default_pdf_batch_size: int = 20
    default_ocr_batch_size: int = 5
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])


@lru_cache
def get_settings() -> Settings:
    return Settings()

