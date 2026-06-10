from datetime import datetime, timezone

from app.db.models import ConversionBatch, ConversionJob


def estimate_units(job: ConversionJob) -> int:
    # Phase 2 has no parser dependencies yet, so units are deterministic estimates.
    bytes_per_unit = 50_000
    return max(1, (job.file.size_bytes + bytes_per_unit - 1) // bytes_per_unit)


def unit_label(job: ConversionJob) -> str:
    return "slide" if "presentation" in job.file.content_type else "page"


def convert_batch_to_markdown(job: ConversionJob, batch: ConversionBatch, source_bytes: bytes) -> str:
    label = unit_label(job)
    heading = f"{label.title()}s {batch.start_unit}-{batch.end_unit}"

    return "\n".join(
        [
            f"## {heading}",
            "",
            f"<!-- {label}: {batch.start_unit} -->",
            "",
            "This section was produced by the Phase 2 deterministic batch converter.",
            "",
            f"- Batch index: {batch.batch_index}",
            f"- Unit range: {batch.start_unit}-{batch.end_unit}",
            f"- Source bytes available to worker: {len(source_bytes)}",
            "",
        ]
    )


def merge_batch_markdown(job: ConversionJob, batch_parts: list[str]) -> str:
    source = job.file
    converted_at = datetime.now(timezone.utc).isoformat()
    label = unit_label(job)

    front_matter = "\n".join(
        [
            "---",
            f'source_filename: "{source.original_filename}"',
            f'source_content_type: "{source.content_type}"',
            f"source_size_bytes: {source.size_bytes}",
            f'converted_at: "{converted_at}"',
            'converter_route: "phase2_stub"',
            f"total_pages: {job.total_units if label == 'page' else 'null'}",
            f"total_slides: {job.total_units if label == 'slide' else 'null'}",
            "ocr_used: false",
            'app_version: "0.1.0"',
            "---",
            "",
            f"# {source.original_filename}",
            "",
        ]
    )

    separator = "\n---\n\n"
    return front_matter + separator.join(batch_parts).strip() + "\n"

