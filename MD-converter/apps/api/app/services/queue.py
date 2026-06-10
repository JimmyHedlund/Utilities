from celery import Celery

from app.core.config import get_settings


def get_celery_client() -> Celery:
    settings = get_settings()
    return Celery(
        "md_converter_api",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )


def enqueue_preflight(job_id: str) -> None:
    celery = get_celery_client()
    celery.send_task("documents.preflight", args=[job_id], queue="preflight")


def enqueue_retry(job_id: str) -> None:
    celery = get_celery_client()
    celery.send_task("documents.retry_failed_batches", args=[job_id], queue="preflight")
