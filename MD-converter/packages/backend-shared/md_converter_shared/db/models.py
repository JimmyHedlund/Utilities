from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from md_converter_shared.db.base import Base


class UploadedFile(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="local")
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    jobs: Mapped[list["ConversionJob"]] = relationship(back_populates="file")


class ConversionJob(Base):
    __tablename__ = "conversion_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    file_id: Mapped[str] = mapped_column(String(64), ForeignKey("files.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="local")
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    output_format: Mapped[str] = mapped_column(String(32), nullable=False, default="markdown")
    converter_route: Mapped[str | None] = mapped_column(String(64))
    total_units: Mapped[int | None] = mapped_column(Integer)
    completed_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    batch_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    options_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    file: Mapped[UploadedFile] = relationship(back_populates="jobs")
    batches: Mapped[list["ConversionBatch"]] = relationship(back_populates="job")
    outputs: Mapped[list["ConversionOutput"]] = relationship(back_populates="job")


class ConversionBatch(Base):
    __tablename__ = "conversion_batches"
    __table_args__ = (UniqueConstraint("job_id", "batch_index", name="uq_conversion_batches_job_index"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), ForeignKey("conversion_jobs.id"), nullable=False)
    batch_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_unit: Mapped[int] = mapped_column(Integer, nullable=False)
    end_unit: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    converter_route: Mapped[str] = mapped_column(String(64), nullable=False)
    celery_task_id: Mapped[str | None] = mapped_column(Text)
    output_storage_key: Mapped[str | None] = mapped_column(Text)
    assets_prefix: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    job: Mapped[ConversionJob] = relationship(back_populates="batches")


class ConversionOutput(Base):
    __tablename__ = "conversion_outputs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), ForeignKey("conversion_jobs.id"), nullable=False)
    markdown_storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    zip_storage_key: Mapped[str | None] = mapped_column(Text)
    assets_prefix: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped[ConversionJob] = relationship(back_populates="outputs")


class JobEvent(Base):
    __tablename__ = "job_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), ForeignKey("conversion_jobs.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    details_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
