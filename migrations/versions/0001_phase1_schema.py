"""Phase 1 operational and historian schema."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_phase1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    op.create_table(
        "production_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("source_key", sa.String(128), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("feature_count", sa.Integer(), nullable=False),
        sa.Column("missing_count", sa.Integer(), nullable=False),
        sa.Column(
            "metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.UniqueConstraint("source", "source_key", name="uq_run_source_key"),
    )
    op.create_table(
        "sensor_readings",
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sensor", sa.String(64), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["production_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("observed_at", "run_id", "sensor"),
    )
    op.execute("SELECT create_hypertable('sensor_readings', 'observed_at', if_not_exists => TRUE)")
    op.create_index("ix_runs_observed_outcome", "production_runs", ["observed_at", "outcome"])
    op.create_index("ix_readings_run", "sensor_readings", ["run_id"])
    op.create_table(
        "investigations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["run_id"], ["production_runs.id"], ondelete="SET NULL"),
    )


def downgrade() -> None:
    op.drop_table("investigations")
    op.drop_table("sensor_readings")
    op.drop_table("production_runs")
