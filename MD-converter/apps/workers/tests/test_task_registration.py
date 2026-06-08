from app.celery_app import celery_app
import app.tasks.document  # noqa: F401


def test_document_tasks_are_registered() -> None:
    expected_tasks = {
        "documents.preflight",
        "documents.split",
        "documents.convert_batch",
        "documents.merge_outputs",
        "documents.cleanup",
        "documents.cancel",
        "documents.retry_failed_batches",
    }

    assert expected_tasks.issubset(set(celery_app.tasks))

