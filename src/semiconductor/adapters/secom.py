"""UCI SECOM dataset adapter.

The source contains 590 anonymized sensor columns. Labels are -1 (pass) and 1
(fail), with a timestamp per observation. The adapter validates alignment,
normalizes timestamps to UTC, preserves missing values, and emits database-ready
production runs and long-form sensor readings.
"""

from __future__ import annotations

import argparse
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from semiconductor.db import get_session_factory
from semiconductor.models import ProductionRun, SensorReading


@dataclass(frozen=True)
class SecomRecord:
    source_key: str
    observed_at: datetime
    outcome: str
    values: tuple[float | None, ...]

    @property
    def missing_count(self) -> int:
        return sum(value is None for value in self.values)


class SecomAdapter:
    sensor_count = 590

    def load(self, features_path: str | Path, labels_path: str | Path) -> Iterator[SecomRecord]:
        features = pd.read_csv(features_path, sep=r"\s+", header=None, na_values=["NaN"])
        labels = pd.read_csv(labels_path, sep=r"\s+", header=None, names=["label", "date", "time"])
        if len(features) != len(labels):
            raise ValueError(
                f"SECOM row mismatch: {len(features)} features vs {len(labels)} labels"
            )
        if features.shape[1] != self.sensor_count:
            raise ValueError(
                f"Expected {self.sensor_count} SECOM sensors, found {features.shape[1]}"
            )

        timestamps = pd.to_datetime(
            labels["date"] + " " + labels["time"], format="%d/%m/%Y %H:%M:%S", utc=True
        )
        for index, (values, label, observed_at) in enumerate(
            zip(
                features.itertuples(index=False, name=None),
                labels["label"],
                timestamps,
                strict=True,
            )
        ):
            clean = tuple(None if pd.isna(value) else float(value) for value in values)
            yield SecomRecord(
                source_key=f"secom-{index:06d}",
                observed_at=observed_at.to_pydatetime(),
                outcome="fail" if int(label) == 1 else "pass",
                values=clean,
            )


def persist_records(session: Session, records: Iterator[SecomRecord], batch_size: int = 100) -> int:
    persisted = 0
    for record in records:
        run_id = uuid.uuid5(uuid.NAMESPACE_URL, f"secom:{record.source_key}")
        statement = (
            insert(ProductionRun)
            .values(
                id=run_id,
                source="secom",
                source_key=record.source_key,
                observed_at=record.observed_at,
                outcome=record.outcome,
                feature_count=len(record.values),
                missing_count=record.missing_count,
                metadata={"dataset": "UCI SECOM", "adapter_version": 1},
            )
            .on_conflict_do_nothing(index_elements=["source", "source_key"])
        )
        result = session.execute(statement)
        if result.rowcount:
            session.add_all(
                [
                    SensorReading(
                        observed_at=record.observed_at,
                        run_id=run_id,
                        sensor=f"sensor_{idx:03d}",
                        value=value,
                    )
                    for idx, value in enumerate(record.values)
                    if value is not None and np.isfinite(value)
                ]
            )
            persisted += 1
        if persisted and persisted % batch_size == 0:
            session.commit()
    session.commit()
    return persisted


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest UCI SECOM files")
    parser.add_argument("--features", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--batch-size", default=100, type=int)
    args = parser.parse_args()
    adapter = SecomAdapter()
    with get_session_factory()() as session:
        count = persist_records(session, adapter.load(args.features, args.labels), args.batch_size)
    print(f"Ingested {count} new SECOM production runs")


if __name__ == "__main__":
    main()
