"""phase1 initial tables

Revision ID: 0001_phase1_initial_tables
Revises:
Create Date: 2026-06-08
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_phase1_initial_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "files",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("original_filename", sa.Text(), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False, unique=True),
        sa.Column("content_type", sa.Text(), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "conversion_jobs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("file_id", sa.String(length=64), sa.ForeignKey("files.id"), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("output_format", sa.String(length=32), nullable=False),
        sa.Column("converter_route", sa.String(length=64), nullable=True),
        sa.Column("total_units", sa.Integer(), nullable=True),
        sa.Column("completed_units", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("batch_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("options_json", sa.JSON(), nullable=False),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "conversion_outputs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("conversion_jobs.id"), nullable=False),
        sa.Column("markdown_storage_key", sa.Text(), nullable=False),
        sa.Column("zip_storage_key", sa.Text(), nullable=True),
        sa.Column("assets_prefix", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "job_events",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("conversion_jobs.id"), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("job_events")
    op.drop_table("conversion_outputs")
    op.drop_table("conversion_jobs")
    op.drop_table("files")

