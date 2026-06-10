from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import ConversionBatch, ConversionJob, ConversionOutput, UploadedFile
from app.tasks import document


class FakeStorage:
    outputs: dict[str, str] = {}

    def get_upload_bytes(self, storage_key: str) -> bytes:
        assert storage_key == "uploads/local/file_1/original.pdf"
        return b"x" * 125_000

    def put_markdown(self, storage_key: str, markdown: str) -> None:
        self.outputs[storage_key] = markdown

    def get_output_text(self, storage_key: str) -> str:
        return self.outputs[storage_key]


def test_phase2_worker_pipeline(monkeypatch) -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    FakeStorage.outputs = {}

    monkeypatch.setattr(document, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(document, "init_db", lambda: None)
    monkeypatch.setattr(document, "StorageService", lambda: FakeStorage())
    monkeypatch.setattr(document.celery_app, "send_task", lambda *args, **kwargs: None)

    with TestingSessionLocal() as db:
        file_record = UploadedFile(
            id="file_1",
            user_id="local",
            original_filename="sample.pdf",
            storage_key="uploads/local/file_1/original.pdf",
            content_type="application/pdf",
            size_bytes=125_000,
            status="uploaded",
        )
        job = ConversionJob(
            id="job_1",
            file_id="file_1",
            user_id="local",
            status="queued",
            output_format="markdown",
            completed_units=0,
            batch_count=0,
            options_json={},
        )
        db.add(file_record)
        db.add(job)
        db.commit()

    assert document.preflight_document.run("job_1")["status"] == "preflighted"
    assert document.split_document.run("job_1")["status"] == "split"

    with TestingSessionLocal() as db:
        batches = db.query(ConversionBatch).order_by(ConversionBatch.batch_index).all()
        assert len(batches) == 1
        batch_ids = [batch.id for batch in batches]

    for batch_id in batch_ids:
        assert document.convert_batch.run(batch_id)["status"] == "succeeded"

    assert document.merge_job_outputs.run("job_1")["status"] == "succeeded"

    with TestingSessionLocal() as db:
        job = db.get(ConversionJob, "job_1")
        output = db.query(ConversionOutput).filter(ConversionOutput.job_id == "job_1").one()
        assert job is not None
        assert job.status == "succeeded"
        assert job.completed_units == job.total_units
        assert output.markdown_storage_key == "jobs/job_1/final/document.md"
        assert "Phase 2 deterministic batch converter" in FakeStorage.outputs[output.markdown_storage_key]

