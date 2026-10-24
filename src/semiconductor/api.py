from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from semiconductor.db import get_session
from semiconductor.schemas import InvestigationCreate, InvestigationView, RunSummary
from semiconductor.services import create_investigation, get_run, list_runs

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health(session: Session = Depends(get_session)) -> dict:
    session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}


@router.get("/runs", response_model=list[RunSummary])
def runs(
    outcome: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    return list_runs(session, outcome, limit)


@router.get("/runs/{run_id}", response_model=RunSummary)
def run(run_id: UUID, session: Session = Depends(get_session)):
    item = get_run(session, run_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Production run not found")
    return item


@router.post(
    "/investigations", response_model=InvestigationView, status_code=status.HTTP_201_CREATED
)
def investigation(payload: InvestigationCreate, session: Session = Depends(get_session)):
    if payload.run_id and get_run(session, payload.run_id) is None:
        raise HTTPException(status_code=404, detail="Production run not found")
    return create_investigation(session, payload.run_id, payload.summary)
