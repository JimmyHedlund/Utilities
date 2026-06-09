from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import UploadedFile
from app.db.session import get_db
from app.models import CompleteUploadResponse, CreateUploadRequest, CreateUploadResponse
from app.services.jobs import create_file_record, mark_file_uploaded
from app.services.storage import StorageService

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_UPLOADS = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
}


@router.post("", response_model=CreateUploadResponse)
def create_upload_session(
    payload: CreateUploadRequest, db: Session = Depends(get_db)
) -> CreateUploadResponse:
    settings = get_settings()
    extension = payload.filename.rsplit(".", 1)[-1].lower() if "." in payload.filename else "bin"

    expected_extension = ALLOWED_UPLOADS.get(payload.content_type)
    if expected_extension is None or extension != expected_extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "unsupported_file_type",
                "message": "Upload a PDF or PPTX file.",
            },
        )

    if payload.size_bytes > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error_code": "file_too_large",
                "message": "This file exceeds the maximum upload size.",
            },
        )

    file_id = f"file_{uuid4().hex}"
    upload_mode = "multipart" if payload.size_bytes >= 100 * 1024 * 1024 else "single"
    storage_key = f"uploads/local/{file_id}/original.{extension}"
    file_record = create_file_record(
        db,
        file_id=file_id,
        filename=payload.filename,
        content_type=payload.content_type,
        size_bytes=payload.size_bytes,
        storage_key=storage_key,
    )
    storage = StorageService()

    return CreateUploadResponse(
        file_id=file_record.id,
        upload_mode=upload_mode,
        upload_urls=[storage.create_upload_url(storage_key, payload.content_type)],
        storage_key=storage_key,
    )


@router.post("/{file_id}/complete", response_model=CompleteUploadResponse)
def complete_upload(file_id: str, db: Session = Depends(get_db)) -> CompleteUploadResponse:
    file_record = db.get(UploadedFile, file_id)
    if file_record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    storage = StorageService()
    expected_size = file_record.size_bytes
    try:
        object_info = storage.head_upload(file_record.storage_key)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "conversion_failed",
                "message": "Uploaded object was not found in storage.",
            },
        ) from exc

    observed_size = int(object_info.get("ContentLength", 0))
    mark_file_uploaded(db, file_id, observed_size)
    return CompleteUploadResponse(
        file_id=file_id,
        status="uploaded",
        checksum_verified=False,
        size_verified=observed_size == expected_size,
    )
