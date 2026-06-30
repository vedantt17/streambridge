from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.readiness import ACTIVE_STATUSES, calculate_readiness

router = APIRouter(prefix="/api/partners", tags=["partners"])


@router.get("")
def list_partners(db: Session = Depends(get_db)) -> list[dict]:
    partners = db.query(models.Partner).order_by(models.Partner.partner_name).all()
    return [_partner_summary(db, partner) for partner in partners]


@router.post("", response_model=schemas.PartnerOut)
def create_partner(payload: schemas.PartnerCreate, db: Session = Depends(get_db)) -> models.Partner:
    existing = (
        db.query(models.Partner)
        .filter(models.Partner.partner_name == payload.partner_name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Partner already exists.")
    partner = models.Partner(**payload.model_dump())
    db.add(partner)
    db.commit()
    db.refresh(partner)
    return partner


@router.get("/{partner_id}")
def get_partner(partner_id: int, db: Session = Depends(get_db)) -> dict:
    partner = db.get(models.Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found.")
    summary = _partner_summary(db, partner)
    feeds = (
        db.query(models.FeedUpload)
        .filter(models.FeedUpload.partner_id == partner_id)
        .order_by(models.FeedUpload.uploaded_at.desc())
        .limit(10)
        .all()
    )
    issues = (
        db.query(models.ValidationError)
        .filter(models.ValidationError.partner_id == partner_id, models.ValidationError.status.in_(ACTIVE_STATUSES))
        .order_by(models.ValidationError.created_at.desc())
        .limit(20)
        .all()
    )
    checks = (
        db.query(models.ApiCheck)
        .filter(models.ApiCheck.partner_id == partner_id)
        .order_by(models.ApiCheck.checked_at.desc())
        .limit(10)
        .all()
    )
    tasks = (
        db.query(models.OnboardingTask)
        .filter(models.OnboardingTask.partner_id == partner_id)
        .order_by(models.OnboardingTask.due_date)
        .all()
    )
    return {
        **summary,
        "feeds": [_feed_dict(feed) for feed in feeds],
        "open_issues": [_issue_dict(issue) for issue in issues],
        "api_checks": [_api_check_dict(check) for check in checks],
        "onboarding_tasks": [_task_dict(task) for task in tasks],
    }


@router.get("/{partner_id}/readiness")
def get_partner_readiness(partner_id: int, db: Session = Depends(get_db)) -> dict:
    partner = db.get(models.Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found.")
    latest = (
        db.query(models.ReadinessScore)
        .filter(models.ReadinessScore.partner_id == partner_id)
        .order_by(models.ReadinessScore.generated_at.desc())
        .first()
    ) or calculate_readiness(db, partner_id)
    return _readiness_dict(latest)


@router.get("/{partner_id}/integration-checklist")
def get_partner_checklist(partner_id: int, db: Session = Depends(get_db)) -> dict:
    from app.services.reports import integration_checklist

    try:
        return integration_checklist(db, partner_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{partner_id}/troubleshooting-summary")
def get_partner_troubleshooting_summary(partner_id: int, db: Session = Depends(get_db)) -> dict:
    from app.services.reports import troubleshooting_summary

    try:
        return troubleshooting_summary(db, partner_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _partner_summary(db: Session, partner: models.Partner) -> dict:
    latest_score = (
        db.query(models.ReadinessScore)
        .filter(models.ReadinessScore.partner_id == partner.partner_id)
        .order_by(models.ReadinessScore.generated_at.desc())
        .first()
    )
    latest_feed = (
        db.query(models.FeedUpload)
        .filter(models.FeedUpload.partner_id == partner.partner_id)
        .order_by(models.FeedUpload.uploaded_at.desc())
        .first()
    )
    active_issues = (
        db.query(models.ValidationError)
        .filter(
            models.ValidationError.partner_id == partner.partner_id,
            models.ValidationError.status.in_(ACTIVE_STATUSES),
        )
        .all()
    )
    max_sla_age = max((datetime.utcnow() - issue.created_at).days for issue in active_issues) if active_issues else 0
    premium_total = (
        db.query(models.ContentItem)
        .filter(models.ContentItem.partner_id == partner.partner_id, models.ContentItem.is_premium.is_(True))
        .count()
    )
    premium_with_entitlement = (
        db.query(models.EntitlementRule)
        .join(models.ContentItem)
        .filter(models.ContentItem.partner_id == partner.partner_id, models.ContentItem.is_premium.is_(True))
        .count()
    )
    entitlement_status = "Complete" if premium_total == 0 or premium_with_entitlement >= premium_total else "Gaps"
    return {
        "partner_id": partner.partner_id,
        "partner_name": partner.partner_name,
        "contact_email": partner.contact_email,
        "integration_status": partner.integration_status,
        "launch_target_date": partner.launch_target_date.isoformat() if partner.launch_target_date else None,
        "region_scope": partner.region_scope,
        "readiness_score": latest_score.readiness_score if latest_score else 0,
        "open_blocker_count": len(active_issues),
        "critical_count": sum(1 for issue in active_issues if issue.severity == "Critical"),
        "high_count": sum(1 for issue in active_issues if issue.severity == "High"),
        "sla_age_days": max_sla_age,
        "last_feed_upload": latest_feed.uploaded_at.isoformat() if latest_feed else None,
        "last_feed_status": latest_feed.parse_status if latest_feed else "No feed",
        "region_coverage": [region.strip() for region in partner.region_scope.split(",") if region.strip()],
        "entitlement_package_status": entitlement_status,
    }


def _feed_dict(feed: models.FeedUpload) -> dict:
    return {
        "feed_id": feed.feed_id,
        "file_name": feed.file_name,
        "file_type": feed.file_type,
        "uploaded_at": feed.uploaded_at.isoformat(),
        "parse_status": feed.parse_status,
        "parser_error": feed.parser_error,
    }


def _issue_dict(issue: models.ValidationError) -> dict:
    return {
        "error_id": issue.error_id,
        "severity": issue.severity,
        "category": issue.category,
        "rule_name": issue.rule_name,
        "error_message": issue.error_message,
        "recommended_fix": issue.recommended_fix,
        "status": issue.status,
        "assigned_owner": issue.assigned_owner,
        "sla_age_days": (datetime.utcnow() - issue.created_at).days,
    }


def _api_check_dict(check: models.ApiCheck) -> dict:
    return {
        "check_id": check.check_id,
        "endpoint": check.endpoint,
        "http_status": check.http_status,
        "latency_ms": check.latency_ms,
        "check_status": check.check_status,
        "checked_at": check.checked_at.isoformat(),
        "error_message": check.error_message,
    }


def _task_dict(task: models.OnboardingTask) -> dict:
    return {
        "task_id": task.task_id,
        "task_name": task.task_name,
        "owner": task.owner,
        "status": task.status,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


def _readiness_dict(score: models.ReadinessScore) -> dict:
    return {
        "score_id": score.score_id,
        "partner_id": score.partner_id,
        "feed_id": score.feed_id,
        "readiness_score": score.readiness_score,
        "critical_count": score.critical_count,
        "high_count": score.high_count,
        "valid_content_pct": score.valid_content_pct,
        "artwork_completion_pct": score.artwork_completion_pct,
        "entitlement_completion_pct": score.entitlement_completion_pct,
        "api_health_score": score.api_health_score,
        "generated_at": score.generated_at.isoformat(),
    }
