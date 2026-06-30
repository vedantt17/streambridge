from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.services.api_simulation import run_partner_api_checks

router = APIRouter(prefix="/api/api-checks", tags=["api-checks"])


@router.post("/run/{partner_id}")
def run_api_checks(partner_id: int, db: Session = Depends(get_db)) -> list[dict]:
    try:
        checks = run_partner_api_checks(db, partner_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [_check_dict(check) for check in checks]


@router.get("/{partner_id}")
def list_api_checks(partner_id: int, db: Session = Depends(get_db)) -> list[dict]:
    partner = db.get(models.Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found.")
    checks = (
        db.query(models.ApiCheck)
        .filter(models.ApiCheck.partner_id == partner_id)
        .order_by(models.ApiCheck.checked_at.desc())
        .limit(100)
        .all()
    )
    return [_check_dict(check) for check in checks]


def _check_dict(check: models.ApiCheck) -> dict:
    return {
        "check_id": check.check_id,
        "partner_id": check.partner_id,
        "endpoint": check.endpoint,
        "http_status": check.http_status,
        "latency_ms": check.latency_ms,
        "check_status": check.check_status,
        "checked_at": check.checked_at.isoformat(),
        "error_message": check.error_message,
    }

