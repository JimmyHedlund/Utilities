from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


class FakeStorage:
    def create_upload_url(self, storage_key: str, content_type: str) -> str:
        return f"http://storage.local/{storage_key}?content_type={content_type}"

    def head_upload(self, storage_key: str) -> dict:
        assert storage_key.endswith("original.pdf")
        return {"ContentLength": 128}


def test_phase1_upload_and_conversion_flow(monkeypatch) -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_db() -> Generator[Session, None, None]:
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr("app.routes.uploads.StorageService", lambda: FakeStorage())
    monkeypatch.setattr("app.routes.conversions.enqueue_preflight", lambda job_id: None)

    try:
        client = TestClient(app)

        upload_response = client.post(
            "/api/uploads",
            json={
                "filename": "sample.pdf",
                "content_type": "application/pdf",
                "size_bytes": 128,
            },
        )
        assert upload_response.status_code == 200
        upload_payload = upload_response.json()
        assert upload_payload["file_id"].startswith("file_")
        assert upload_payload["upload_urls"][0].startswith("http://storage.local/")

        complete_response = client.post(f"/api/uploads/{upload_payload['file_id']}/complete")
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "uploaded"
        assert complete_response.json()["size_verified"] is True

        conversion_response = client.post(
            "/api/conversions",
            json={
                "file_id": upload_payload["file_id"],
                "output_format": "markdown",
                "options": {
                    "extract_images": True,
                    "ocr": "auto",
                    "preserve_page_breaks": True,
                    "preferred_converter": "auto",
                },
            },
        )
        assert conversion_response.status_code == 200
        conversion_payload = conversion_response.json()
        assert conversion_payload["status"] == "queued"

        job_response = client.get(f"/api/conversions/{conversion_payload['job_id']}")
        assert job_response.status_code == 200
        assert job_response.json()["file"]["filename"] == "sample.pdf"

        list_response = client.get("/api/conversions")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
    finally:
        app.dependency_overrides.clear()
