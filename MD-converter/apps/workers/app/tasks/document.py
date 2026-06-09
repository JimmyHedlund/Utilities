from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import joinedload

from app.celery_app import celery_app
from app.converters.phase1 import convert_to_markdown
from app.db.models import ConversionJob, ConversionOutput, JobEvent
from app.db.session import SessionLocal, init_db
from app.storage.s3 import StorageService


@celery_app.task(name="documents.convert_job")
def convert_job(job_id: str) -> dict[str, str]:
    init_db()
    storage = StorageService()

    with SessionLocal() as db:
        job = (
            db.query(ConversionJob)
            .options(joinedload(ConversionJob.file))
            .filter(ConversionJob.id == job_id)
            .first()
        )
        if job is None:
            return {"job_id": job_id, "status": "missing"}

        try:
            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            db.add(
                JobEvent(
                    id=f"evt_{uuid4().hex}",
                    job_id=job.id,
                    event_type="job_started",
                    message="Phase 1 conversion started.",
                    details_json={},
                )
            )
            db.commit()

            source_bytes = storage.get_upload_bytes(job.file.storage_key)
            markdown = convert_to_markdown(job, source_bytes)
            output_key = f"jobs/{job.id}/final/document.md"
            storage.put_markdown(output_key, markdown)

            job.status = "succeeded"
            job.completed_units = 1
            job.finished_at = datetime.now(timezone.utc)
            db.add(
                ConversionOutput(
                    id=f"out_{uuid4().hex}",
                    job_id=job.id,
                    markdown_storage_key=output_key,
                    zip_storage_key=None,
                    assets_prefix=None,
                    metadata_json={"converter_route": "phase1_stub"},
                )
            )
            db.add(
                JobEvent(
                    id=f"evt_{uuid4().hex}",
                    job_id=job.id,
                    event_type="job_succeeded",
                    message="Phase 1 conversion completed.",
                    details_json={"markdown_storage_key": output_key},
                )
            )
            db.commit()
            return {"job_id": job.id, "status": "succeeded"}
        except Exception as exc:
            job.status = "failed"
            job.error_code = "conversion_failed"
            job.error_message = str(exc)
            job.finished_at = datetime.now(timezone.utc)
            db.add(
                JobEvent(
                    id=f"evt_{uuid4().hex}",
                    job_id=job.id,
                    event_type="job_failed",
                    message="Phase 1 conversion failed.",
                    details_json={"error": str(exc)},
                )
            )
            db.commit()
            raise


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
