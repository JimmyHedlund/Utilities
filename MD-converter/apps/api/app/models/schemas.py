from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


JobStatus = Literal[
    "uploaded",
    "queued",
    "preflighting",
    "splitting",
    "running",
    "merging",
    "succeeded",
    "failed",
    "cancelling",
    "cancelled",
    "retrying",
]

BatchStatus = Literal["queued", "running", "succeeded", "failed", "cancelled", "skipped"]

UserFacingErrorCode = Literal[
    "unsupported_file_type",
    "file_too_large",
    "too_many_pages",
    "too_many_slides",
    "encrypted_pdf",
    "corrupt_file",
    "conversion_timeout",
    "conversion_failed",
    "partial_conversion",
    "not_implemented",
]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app: str
    version: str


class CreateUploadRequest(BaseModel):
    filename: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    size_bytes: int = Field(gt=0)


class CreateUploadResponse(BaseModel):
    file_id: str
    upload_mode: Literal["single", "multipart"]
    upload_urls: list[str]
    storage_key: str


class CompleteUploadResponse(BaseModel):
    file_id: str
    status: Literal["uploaded"]
    checksum_verified: bool
    size_verified: bool = True


class ConversionOptions(BaseModel):
    extract_images: bool = True
    ocr: Literal["auto", "enabled", "disabled"] = "auto"
    preserve_page_breaks: bool = True
    preferred_converter: Literal["auto", "docling", "pymupdf4llm", "markitdown"] = "auto"


class CreateConversionRequest(BaseModel):
    file_id: str
    output_format: Literal["markdown"] = "markdown"
    options: ConversionOptions = Field(default_factory=ConversionOptions)


class CreateConversionResponse(BaseModel):
    job_id: str
    status: JobStatus


class FileSummary(BaseModel):
    filename: str
    content_type: str
    size_bytes: int


class ProgressSummary(BaseModel):
    total_units: int
    completed_units: int
    percent: float
    current_stage: str


class BatchCounts(BaseModel):
    total: int
    queued: int
    running: int
    succeeded: int
    failed: int


class ConversionResult(BaseModel):
    markdown_url: str | None = None
    zip_url: str | None = None
    expires_at: datetime | None = None


class ConversionError(BaseModel):
    code: UserFacingErrorCode
    message: str


class ConversionJobResponse(BaseModel):
    job_id: str
    status: JobStatus
    file: FileSummary
    progress: ProgressSummary
    batches: BatchCounts
    result: ConversionResult | None
    error: ConversionError | None
    created_at: datetime
    updated_at: datetime


class ConversionDownloadResponse(BaseModel):
    job_id: str
    markdown_url: str
    zip_url: str | None
    expires_at: datetime


class ErrorDetail(BaseModel):
    error_code: UserFacingErrorCode
    message: str


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
