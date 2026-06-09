from celery import Celery
from kombu import Queue

from app.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "md_converter_workers",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.document"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_queues=(
        Queue("preflight"),
        Queue("fast"),
        Queue("layout"),
        Queue("ocr"),
        Queue("pptx"),
        Queue("merge"),
        Queue("cleanup"),
    ),
    task_routes={
        "documents.preflight": {"queue": "preflight"},
        "documents.split": {"queue": "preflight"},
        "documents.convert_job": {"queue": "layout"},
        "documents.convert_batch": {"queue": "layout"},
        "documents.merge_outputs": {"queue": "merge"},
        "documents.cleanup": {"queue": "cleanup"},
        "documents.cancel": {"queue": "preflight"},
        "documents.retry_failed_batches": {"queue": "preflight"},
    },
)
