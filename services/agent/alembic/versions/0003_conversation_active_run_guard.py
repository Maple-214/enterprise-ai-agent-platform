"""prevent concurrent active runs per conversation

Revision ID: 0003_conversation_active_run_guard
Revises: 0002_conversation_run_domains
"""
from alembic import op

revision = "0003_conversation_active_run_guard"
down_revision = "0002_conversation_run_domains"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_runs_conversation_status",
        "runs",
        ["conversation_id", "status"],
        unique=False,
    )

    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_runs_one_active_per_conversation
        ON runs (conversation_id)
        WHERE status IN ('queued', 'running')
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_runs_one_active_per_conversation")
    op.drop_index("ix_runs_conversation_status", table_name="runs")
