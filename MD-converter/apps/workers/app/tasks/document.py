from app.celery_app import celery_app


@celery_app.task(name="documents.preflight")
def preflight_document(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "status": "preflight_stubbed"}


@celery_app.task(name="documents.split")
def split_document(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "status": "split_stubbed"}


@celery_app.task(name="documents.convert_batch")
def convert_batch(batch_id: str) -> dict[str, str]:
    return {"batch_id": batch_id, "status": "conversion_stubbed"}


@celery_app.task(name="documents.merge_outputs")
def merge_job_outputs(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "status": "merge_stubbed"}


@celery_app.task(name="documents.cleanup")
def cleanup_job(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "status": "cleanup_stubbed"}


@celery_app.task(name="documents.cancel")
def cancel_job(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "status": "cancel_stubbed"}


@celery_app.task(name="documents.retry_failed_batches")
def retry_failed_batches(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "status": "retry_stubbed"}

