from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.models import (
    BatchCounts,
    ConversionJobResponse,
    CreateConversionRequest,
    CreateConversionResponse,
    FileSummary,
    ProgressSummary,
)
from app.models.schemas import utc_now

router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.post("", response_model=CreateConversionResponse)
def create_conversion(payload: CreateConversionRequest) -> CreateConversionResponse:
    _ = payload
    return CreateConversionResponse(job_id=f"job_{uuid4().hex}", status="queued")


@router.get("", response_model=list[ConversionJobResponse])
def list_conversions() -> list[ConversionJobResponse]:
    return []


@router.get("/{job_id}", response_model=ConversionJobResponse)
def get_conversion(job_id: str) -> ConversionJobResponse:
    now = utc_now()
    return ConversionJobResponse(
        job_id=job_id,
        status="queued",
        file=FileSummary(
            filename="example.pdf",
            content_type="application/pdf",
            size_bytes=157_286_400,
        ),
        progress=ProgressSummary(
            total_units=0,
            completed_units=0,
            percent=0.0,
            current_stage="queued",
        ),
        batches=BatchCounts(total=0, queued=0, running=0, succeeded=0, failed=0),
        result=None,
        error=None,
        created_at=now,
        updated_at=now,
    )


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


@router.get("/{job_id}/download")
def download_conversion(job_id: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "job_id": job_id,
            "error_code": "not_implemented",
            "message": "Downloads require final output storage integration.",
        },
    )

