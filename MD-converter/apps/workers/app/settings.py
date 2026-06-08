from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    app_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://md_converter:md_converter@localhost:5432/md_converter"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket_uploads: str = "uploads"
    s3_bucket_outputs: str = "outputs"
    default_pdf_batch_size: int = 20
    default_ocr_batch_size: int = 5


@lru_cache
def get_settings() -> WorkerSettings:
    return WorkerSettings()

