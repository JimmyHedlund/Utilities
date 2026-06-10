from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import joinedload

from app.celery_app import celery_app
from app.converters.phase1 import convert_to_markdown
from app.converters.phase2 import convert_batch_to_markdown, estimate_units, merge_batch_markdown
from app.db.models import ConversionBatch, ConversionJob, ConversionOutput, JobEvent
from app.db.session import SessionLocal, init_db
from app.settings import get_settings
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
    init_db()
    with SessionLocal() as db:
        job = (
            db.query(ConversionJob)
            .options(joinedload(ConversionJob.file))
            .filter(ConversionJob.id == job_id)
            .first()
        )
        if job is None:
            return {"job_id": job_id, "status": "missing"}
        if job.status == "cancelled":
            return {"job_id": job.id, "status": "cancelled"}

        job.status = "preflighting"
        job.started_at = job.started_at or datetime.now(timezone.utc)
        job.converter_route = "phase2_stub"
        job.total_units = estimate_units(job)
        db.add(
            JobEvent(
                id=f"evt_{uuid4().hex}",
                job_id=job.id,
                event_type="job_preflighted",
                message="Phase 2 deterministic preflight completed.",
                details_json={"total_units": job.total_units, "converter_route": job.converter_route},
            )
        )
        db.commit()

    celery_app.send_task("documents.split", args=[job_id], queue="preflight")
    return {"job_id": job_id, "status": "preflighted"}


@celery_app.task(name="documents.split")
def split_document(job_id: str) -> dict[str, str]:
    init_db()
    settings = get_settings()
    batch_ids: list[str] = []

    with SessionLocal() as db:
        job = (
            db.query(ConversionJob)
            .options(joinedload(ConversionJob.file))
            .filter(ConversionJob.id == job_id)
            .first()
        )
        if job is None:
            return {"job_id": job_id, "status": "missing"}
        if job.status == "cancelled":
            return {"job_id": job.id, "status": "cancelled"}

        existing_batches = db.query(ConversionBatch).filter(ConversionBatch.job_id == job.id).all()
        if existing_batches:
            batch_ids = [batch.id for batch in existing_batches if batch.status in {"queued", "failed"}]
        else:
            job.status = "splitting"
            total_units = job.total_units or estimate_units(job)
            batch_size = settings.default_pdf_batch_size
            batch_index = 0
            for start_unit in range(1, total_units + 1, batch_size):
                end_unit = min(start_unit + batch_size - 1, total_units)
                batch = ConversionBatch(
                    id=f"batch_{uuid4().hex}",
                    job_id=job.id,
                    batch_index=batch_index,
                    start_unit=start_unit,
                    end_unit=end_unit,
                    status="queued",
                    converter_route=job.converter_route or "phase2_stub",
                )
                db.add(batch)
                batch_ids.append(batch.id)
                batch_index += 1

            job.batch_count = len(batch_ids)
            db.add(
                JobEvent(
                    id=f"evt_{uuid4().hex}",
                    job_id=job.id,
                    event_type="job_split",
                    message="Conversion job split into batches.",
                    details_json={"batch_count": job.batch_count},
                )
            )

        job.status = "running"
        db.commit()

    for batch_id in batch_ids:
        celery_app.send_task("documents.convert_batch", args=[batch_id], queue="layout")

    return {"job_id": job_id, "status": "split", "batch_count": str(len(batch_ids))}


@celery_app.task(name="documents.convert_batch")
def convert_batch(batch_id: str) -> dict[str, str]:
    init_db()
    storage = StorageService()

    with SessionLocal() as db:
        batch = (
            db.query(ConversionBatch)
            .options(joinedload(ConversionBatch.job).joinedload(ConversionJob.file))
            .filter(ConversionBatch.id == batch_id)
            .first()
        )
        if batch is None:
            return {"batch_id": batch_id, "status": "missing"}
        if batch.status == "cancelled" or batch.job.status == "cancelled":
            return {"batch_id": batch.id, "status": "cancelled"}

        try:
            batch.status = "running"
            batch.started_at = datetime.now(timezone.utc)
            db.commit()

            source_bytes = storage.get_upload_bytes(batch.job.file.storage_key)
            markdown = convert_batch_to_markdown(batch.job, batch, source_bytes)
            output_key = f"jobs/{batch.job_id}/batches/{batch.batch_index}/part.md"
            storage.put_markdown(output_key, markdown)

            batch.status = "succeeded"
            batch.output_storage_key = output_key
            batch.finished_at = datetime.now(timezone.utc)
            batch.job.completed_units = _completed_units_for_job(db, batch.job_id)
            db.commit()
        except Exception as exc:
            batch.status = "failed"
            batch.error_code = "conversion_failed"
            batch.error_message = str(exc)
            batch.finished_at = datetime.now(timezone.utc)
            batch.job.status = "failed"
            batch.job.error_code = "conversion_failed"
            batch.job.error_message = str(exc)
            db.add(
                JobEvent(
                    id=f"evt_{uuid4().hex}",
                    job_id=batch.job_id,
                    event_type="batch_failed",
                    message="Batch conversion failed.",
                    details_json={"batch_id": batch.id, "error": str(exc)},
                )
            )
            db.commit()
            raise

        all_batches = db.query(ConversionBatch).filter(ConversionBatch.job_id == batch.job_id).all()
        if all_batches and all(item.status == "succeeded" for item in all_batches):
            celery_app.send_task("documents.merge_outputs", args=[batch.job_id], queue="merge")

    return {"batch_id": batch_id, "status": "succeeded"}


@celery_app.task(name="documents.merge_outputs")
def merge_job_outputs(job_id: str) -> dict[str, str]:
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
        if job.status == "cancelled":
            return {"job_id": job.id, "status": "cancelled"}
        if job.status == "succeeded":
            return {"job_id": job.id, "status": "succeeded"}

        batches = (
            db.query(ConversionBatch)
            .filter(ConversionBatch.job_id == job.id)
            .order_by(ConversionBatch.batch_index.asc())
            .all()
        )
        if not batches or any(batch.status != "succeeded" for batch in batches):
            return {"job_id": job.id, "status": "waiting_for_batches"}

        job.status = "merging"
        db.commit()

        batch_parts = [storage.get_output_text(batch.output_storage_key or "") for batch in batches]
        markdown = merge_batch_markdown(job, batch_parts)
        output_key = f"jobs/{job.id}/final/document.md"
        storage.put_markdown(output_key, markdown)

        job.status = "succeeded"
        job.completed_units = job.total_units or _completed_units_for_job(db, job.id)
        job.finished_at = datetime.now(timezone.utc)
        db.add(
            ConversionOutput(
                id=f"out_{uuid4().hex}",
                job_id=job.id,
                markdown_storage_key=output_key,
                zip_storage_key=None,
                assets_prefix=None,
                metadata_json={"converter_route": "phase2_stub", "batch_count": len(batches)},
            )
        )
        db.add(
            JobEvent(
                id=f"evt_{uuid4().hex}",
                job_id=job.id,
                event_type="job_succeeded",
                message="Phase 2 merge completed.",
                details_json={"markdown_storage_key": output_key, "batch_count": len(batches)},
            )
        )
        db.commit()

    return {"job_id": job_id, "status": "succeeded"}


@celery_app.task(name="documents.cleanup")
def cleanup_job(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "status": "cleanup_stubbed"}


@celery_app.task(name="documents.cancel")
def cancel_job(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "status": "cancel_stubbed"}


@celery_app.task(name="documents.retry_failed_batches")
def retry_failed_batches(job_id: str) -> dict[str, str]:
    init_db()
    retried = 0
    with SessionLocal() as db:
        job = db.query(ConversionJob).filter(ConversionJob.id == job_id).first()
        if job is None:
            return {"job_id": job_id, "status": "missing"}

        batches = db.query(ConversionBatch).filter(ConversionBatch.job_id == job.id).all()
        targets = [batch for batch in batches if batch.status in {"queued", "failed"}]
        job.status = "running"
        job.error_code = None
        job.error_message = None
        db.commit()

    for batch in targets:
        retried += 1
        celery_app.send_task("documents.convert_batch", args=[batch.id], queue="layout")

    return {"job_id": job_id, "status": "retrying", "batch_count": str(retried)}


def _completed_units_for_job(db, job_id: str) -> int:
    succeeded = db.query(ConversionBatch).filter(
        ConversionBatch.job_id == job_id,
        ConversionBatch.status == "succeeded",
    )
    return sum(batch.end_unit - batch.start_unit + 1 for batch in succeeded)
