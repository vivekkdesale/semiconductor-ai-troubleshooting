from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from semiconductor.models import Investigation, ProductionRun


def list_runs(session: Session, outcome: str | None, limit: int) -> list[ProductionRun]:
    query = select(ProductionRun).order_by(ProductionRun.observed_at.desc()).limit(limit)
    if outcome:
        query = query.where(ProductionRun.outcome == outcome)
    return list(session.scalars(query))


def get_run(session: Session, run_id: UUID) -> ProductionRun | None:
    return session.get(ProductionRun, run_id)


def create_investigation(session: Session, run_id: UUID | None, summary: str) -> Investigation:
    item = Investigation(run_id=run_id, summary=summary)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
