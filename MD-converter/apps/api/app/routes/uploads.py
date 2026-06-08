from uuid import uuid4

from fastapi import APIRouter

from app.core.config import get_settings
from app.models import CompleteUploadResponse, CreateUploadRequest, CreateUploadResponse

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", response_model=CreateUploadResponse)
def create_upload_session(payload: CreateUploadRequest) -> CreateUploadResponse:
    settings = get_settings()
    file_id = f"file_{uuid4().hex}"
    extension = payload.filename.rsplit(".", 1)[-1].lower() if "." in payload.filename else "bin"
    upload_mode = "multipart" if payload.size_bytes >= 100 * 1024 * 1024 else "single"
    storage_key = f"uploads/local/{file_id}/original.{extension}"

    return CreateUploadResponse(
        file_id=file_id,
        upload_mode=upload_mode,
        upload_urls=[
            f"{settings.s3_endpoint_url}/{settings.s3_bucket_uploads}/{storage_key}?placeholder=true"
        ],
        storage_key=storage_key,
    )


@router.post("/{file_id}/complete", response_model=CompleteUploadResponse)
def complete_upload(file_id: str) -> CompleteUploadResponse:
    return CompleteUploadResponse(file_id=file_id, status="uploaded", checksum_verified=False)

