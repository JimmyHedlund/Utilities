from datetime import datetime, timezone

from app.db.models import ConversionJob


def convert_to_markdown(job: ConversionJob, source_bytes: bytes) -> str:
    source = job.file
    converted_at = datetime.now(timezone.utc).isoformat()

    return "\n".join(
        [
            "---",
            f'source_filename: "{source.original_filename}"',
            f'source_content_type: "{source.content_type}"',
            f"source_size_bytes: {source.size_bytes}",
            f'converted_at: "{converted_at}"',
            'converter_route: "phase1_stub"',
            "total_pages: null",
            "total_slides: null",
            "ocr_used: false",
            'app_version: "0.1.0"',
            "---",
            "",
            f"# {source.original_filename}",
            "",
            "This Markdown file was produced by the Phase 1 local conversion path.",
            "",
            "Real document parsing is implemented in Phase 3. This phase validates upload, storage, job state, worker execution, and download flow.",
            "",
            f"- Input bytes received: {len(source_bytes)}",
            f"- Job ID: `{job.id}`",
            f"- File ID: `{source.id}`",
            "",
        ]
    )

