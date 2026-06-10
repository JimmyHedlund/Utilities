from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.models import ConversionBatch, ConversionJob, ConversionOutput, JobEvent, UploadedFile
from app.models import (
    BatchCounts,
    ConversionJobResponse,
    ConversionResult,
    CreateConversionRequest,
    FileSummary,
    ProgressSummary,
)


def create_file_record(
    db: Session,
    *,
    file_id: str,
    filename: str,
    content_type: str,
    size_bytes: int,
    storage_key: str,
) -> UploadedFile:
    file_record = UploadedFile(
        id=file_id,
        user_id="local",
        original_filename=filename,
        storage_key=storage_key,
        content_type=content_type,
        size_bytes=size_bytes,
        status="created",
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    return file_record


def mark_file_uploaded(db: Session, file_id: str, observed_size: int) -> UploadedFile | None:
    file_record = db.get(UploadedFile, file_id)
    if file_record is None:
        return None

    file_record.status = "uploaded"
    file_record.size_bytes = observed_size
    db.commit()
    db.refresh(file_record)
    return file_record


def create_conversion_job(db: Session, payload: CreateConversionRequest) -> ConversionJob | None:
    file_record = db.get(UploadedFile, payload.file_id)
    if file_record is None or file_record.status != "uploaded":
        return None

    job = ConversionJob(
        id=f"job_{uuid4().hex}",
        file_id=file_record.id,
        user_id=file_record.user_id,
        status="queued",
        output_format=payload.output_format,
        converter_route="phase2_stub",
        total_units=None,
        completed_units=0,
        batch_count=0,
        options_json=payload.options.model_dump(),
    )
    db.add(job)
    db.add(
        JobEvent(
            id=f"evt_{uuid4().hex}",
            job_id=job.id,
            event_type="job_created",
            message="Conversion job queued.",
            details_json={"file_id": file_record.id},
        )
    )
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> ConversionJob | None:
    return db.scalars(
        select(ConversionJob)
        .where(ConversionJob.id == job_id)
        .options(
            joinedload(ConversionJob.file),
            selectinload(ConversionJob.batches),
            selectinload(ConversionJob.outputs),
        )
    ).first()


def list_jobs(db: Session) -> list[ConversionJob]:
    return list(
        db.scalars(
            select(ConversionJob)
            .options(
                joinedload(ConversionJob.file),
                selectinload(ConversionJob.batches),
                selectinload(ConversionJob.outputs),
            )
            .order_by(ConversionJob.created_at.desc())
        )
        .unique()
        .all()
    )


def get_latest_output(db: Session, job_id: str) -> ConversionOutput | None:
    return db.scalars(
        select(ConversionOutput)
        .where(ConversionOutput.job_id == job_id)
        .order_by(ConversionOutput.created_at.desc())
    ).first()


def cancel_job(db: Session, job_id: str) -> ConversionJob | None:
    job = get_job(db, job_id)
    if job is None:
        return None

    if job.status in {"succeeded", "failed", "cancelled"}:
        return job

    job.status = "cancelled"
    job.finished_at = datetime.now(timezone.utc)
    for batch in job.batches:
        if batch.status in {"queued", "running"}:
            batch.status = "cancelled"
    db.add(
        JobEvent(
            id=f"evt_{uuid4().hex}",
            job_id=job.id,
            event_type="job_cancelled",
            message="Conversion job cancelled.",
            details_json={},
        )
    )
    db.commit()
    db.refresh(job)
    return job


def mark_failed_batches_for_retry(db: Session, job_id: str) -> ConversionJob | None:
    job = get_job(db, job_id)
    if job is None:
        return None

    failed_batches = [batch for batch in job.batches if batch.status == "failed"]
    if not failed_batches and job.status != "failed":
        return job

    job.status = "retrying"
    job.error_code = None
    job.error_message = None
    for batch in failed_batches:
        batch.status = "queued"
        batch.retry_count += 1
        batch.error_code = None
        batch.error_message = None
    db.add(
        JobEvent(
            id=f"evt_{uuid4().hex}",
            job_id=job.id,
            event_type="job_retrying",
            message="Failed batches queued for retry.",
            details_json={"failed_batch_count": len(failed_batches)},
        )
    )
    db.commit()
    db.refresh(job)
    return job


def job_to_response(job: ConversionJob, download_url: str | None = None) -> ConversionJobResponse:
    output = job.outputs[-1] if job.outputs else None
    total_units = job.total_units or 1
    completed_units = job.completed_units
    if job.status == "succeeded":
        completed_units = total_units
    percent = round((completed_units / total_units) * 100, 2) if total_units else 0.0
    if job.status == "queued":
        percent = 0.0
    elif job.status == "preflighting":
        percent = max(percent, 20.0)
    elif job.status == "splitting":
        percent = max(percent, 25.0)
    elif job.status == "running":
        percent = max(percent, 30.0)
    elif job.status == "merging":
        percent = max(percent, 90.0)
    elif job.status == "succeeded":
        percent = 100.0

    batch_counts = _batch_counts(job.batches)
    expires_at = None
    if output and download_url:
        expires_at = datetime.now(timezone.utc)

    return ConversionJobResponse(
        job_id=job.id,
        status=job.status,
        file=FileSummary(
            filename=job.file.original_filename,
            content_type=job.file.content_type,
            size_bytes=job.file.size_bytes,
        ),
        progress=ProgressSummary(
            total_units=total_units,
            completed_units=completed_units,
            percent=percent,
            current_stage="complete" if job.status == "succeeded" else job.status,
        ),
        batches=batch_counts,
        result=ConversionResult(markdown_url=download_url, zip_url=None, expires_at=expires_at)
        if output
        else None,
        error={"code": job.error_code, "message": job.error_message}
        if job.error_code and job.error_message
        else None,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def _batch_counts(batches: list[ConversionBatch]) -> BatchCounts:
    return BatchCounts(
        total=len(batches),
        queued=sum(1 for batch in batches if batch.status == "queued"),
        running=sum(1 for batch in batches if batch.status == "running"),
        succeeded=sum(1 for batch in batches if batch.status == "succeeded"),
        failed=sum(1 for batch in batches if batch.status == "failed"),
    )
