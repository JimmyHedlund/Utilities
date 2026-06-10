"""phase2 conversion batches

Revision ID: 0002_phase2_conversion_batches
Revises: 0001_phase1_initial_tables
Create Date: 2026-06-09
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_phase2_conversion_batches"
down_revision = "0001_phase1_initial_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversion_batches",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("conversion_jobs.id"), nullable=False),
        sa.Column("batch_index", sa.Integer(), nullable=False),
        sa.Column("start_unit", sa.Integer(), nullable=False),
        sa.Column("end_unit", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("converter_route", sa.String(length=64), nullable=False),
        sa.Column("celery_task_id", sa.Text(), nullable=True),
        sa.Column("output_storage_key", sa.Text(), nullable=True),
        sa.Column("assets_prefix", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("job_id", "batch_index", name="uq_conversion_batches_job_index"),
    )


def downgrade() -> None:
    op.drop_table("conversion_batches")

