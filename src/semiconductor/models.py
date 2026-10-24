import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from semiconductor.db import Base


class ProductionRun(Base):
    __tablename__ = "production_runs"
    __table_args__ = (UniqueConstraint("source", "source_key", name="uq_run_source_key"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(64))
    source_key: Mapped[str] = mapped_column(String(128))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    outcome: Mapped[str] = mapped_column(String(16), index=True)
    feature_count: Mapped[int] = mapped_column(Integer)
    missing_count: Mapped[int] = mapped_column(Integer)
    run_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    readings: Mapped[list["SensorReading"]] = relationship(cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production_runs.id", ondelete="CASCADE"), primary_key=True
    )
    sensor: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production_runs.id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(String(32), default="open")
    summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
