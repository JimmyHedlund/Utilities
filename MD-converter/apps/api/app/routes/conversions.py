import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    ConversionDownloadResponse,
    ConversionJobResponse,
    CreateConversionRequest,
    CreateConversionResponse,
)
from app.services.jobs import create_conversion_job, get_job, get_latest_output, job_to_response, list_jobs
from app.services.queue import enqueue_small_conversion
from app.services.storage import StorageService

router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.post("", response_model=CreateConversionResponse)
def create_conversion(
    payload: CreateConversionRequest, db: Session = Depends(get_db)
) -> CreateConversionResponse:
    job = create_conversion_job(db, payload)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "conversion_failed",
                "message": "Uploaded file was not found or has not been completed.",
            },
        )

    enqueue_small_conversion(job.id)
    return CreateConversionResponse(job_id=job.id, status=job.status)


@router.get("", response_model=list[ConversionJobResponse])
def list_conversions(db: Session = Depends(get_db)) -> list[ConversionJobResponse]:
    return [job_to_response(job) for job in list_jobs(db)]


@router.get("/{job_id}", response_model=ConversionJobResponse)
def get_conversion(job_id: str, db: Session = Depends(get_db)) -> ConversionJobResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    return job_to_response(job)


@router.get("/{job_id}/events")
def stream_conversion_events(job_id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    payload = job_to_response(job).model_dump(mode="json")
    event = f"event: status\ndata: {json.dumps(payload)}\n\n"
    return StreamingResponse(iter([event]), media_type="text/event-stream")


@router.post("/{job_id}/cancel")
def cancel_conversion(job_id: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "job_id": job_id,
            "error_code": "not_implemented",
            "message": "Cancellation requires persistent job state and queue integration.",
        },
    )


@router.post("/{job_id}/retry")
def retry_conversion(job_id: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "job_id": job_id,
            "error_code": "not_implemented",
            "message": "Retry requires batch state and queue integration.",
        },
    )


@router.get("/{job_id}/download", response_model=ConversionDownloadResponse)
def download_conversion(job_id: str, db: Session = Depends(get_db)) -> ConversionDownloadResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    if job.status != "succeeded":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job has not succeeded.")

    output = get_latest_output(db, job_id)
    if output is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Output not found.")

    url, ttl = StorageService().create_download_url(output.markdown_storage_key)
    return ConversionDownloadResponse(
        job_id=job_id,
        markdown_url=url,
        zip_url=None,
        expires_at=datetime.now(timezone.utc) + ttl,
    )
