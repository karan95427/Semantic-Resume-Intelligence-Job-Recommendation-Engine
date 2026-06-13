from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260613_02"
down_revision = "20260613_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "explanation_cache",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("facts_hash", sa.String(length=64), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False),
        sa.Column("provider_name", sa.String(length=64), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("input_facts", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "facts_hash",
            "prompt_version",
            "provider_name",
            "model_name",
            name="uq_explanation_cache_key",
        ),
    )
    op.create_index(
        op.f("ix_explanation_cache_facts_hash"),
        "explanation_cache",
        ["facts_hash"],
        unique=False,
    )
    op.create_index(
        op.f("ix_explanation_cache_job_id"),
        "explanation_cache",
        ["job_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_explanation_cache_job_id"), table_name="explanation_cache")
    op.drop_index(
        op.f("ix_explanation_cache_facts_hash"),
        table_name="explanation_cache",
    )
    op.drop_table("explanation_cache")
