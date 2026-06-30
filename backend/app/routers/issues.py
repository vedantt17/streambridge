from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.get("/triage")
def triage_queue(
    severity: str | None = Query(default=None),
    category: str | None = Query(default=None),
    partner_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = db.query(models.ValidationError, models.Partner.partner_name, models.ContentItem.title).join(
        models.Partner, models.ValidationError.partner_id == models.Partner.partner_id
    ).outerjoin(models.ContentItem, models.ValidationError.content_id == models.ContentItem.content_id)
    if severity:
        query = query.filter(models.ValidationError.severity == severity)
    if category:
        query = query.filter(models.ValidationError.category == category)
    if partner_id:
        query = query.filter(models.ValidationError.partner_id == partner_id)
    if status:
        query = query.filter(models.ValidationError.status == status)
    rows = query.order_by(models.ValidationError.created_at.desc()).limit(500).all()
    return [_issue_row(issue, partner_name, title) for issue, partner_name, title in rows]


@router.patch("/{issue_id}")
def update_issue(issue_id: int, payload: schemas.IssuePatch, db: Session = Depends(get_db)) -> dict:
    issue = db.get(models.ValidationError, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")
    if payload.status:
        issue.status = payload.status
        issue.resolved_at = datetime.utcnow() if payload.status == "Resolved" else None
    if payload.assigned_owner:
        issue.assigned_owner = payload.assigned_owner
    if payload.resolution_notes is not None:
        issue.resolution_notes = payload.resolution_notes
    db.commit()
    db.refresh(issue)
    partner = db.get(models.Partner, issue.partner_id)
    content = db.get(models.ContentItem, issue.content_id) if issue.content_id else None
    return _issue_row(issue, partner.partner_name if partner else "Unknown", content.title if content else None)


def _issue_row(issue: models.ValidationError, partner_name: str, title: str | None) -> dict:
    return {
        "error_id": issue.error_id,
        "partner_id": issue.partner_id,
        "partner_name": partner_name,
        "feed_id": issue.feed_id,
        "content_id": issue.content_id,
        "content_title": title,
        "severity": issue.severity,
        "category": issue.category,
        "rule_name": issue.rule_name,
        "error_message": issue.error_message,
        "recommended_fix": issue.recommended_fix,
        "assigned_owner": issue.assigned_owner,
        "status": issue.status,
        "resolution_notes": issue.resolution_notes,
        "sla_age_days": (datetime.utcnow() - issue.created_at).days,
        "created_at": issue.created_at.isoformat(),
        "resolved_at": issue.resolved_at.isoformat() if issue.resolved_at else None,
    }

