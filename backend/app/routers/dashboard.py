from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.routers.partners import _partner_summary
from app.services.readiness import ACTIVE_STATUSES

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict:
    partners = db.query(models.Partner).all()
    latest_scores = []
    for partner in partners:
        score = (
            db.query(models.ReadinessScore)
            .filter(models.ReadinessScore.partner_id == partner.partner_id)
            .order_by(models.ReadinessScore.generated_at.desc())
            .first()
        )
        if score:
            latest_scores.append(score.readiness_score)

    active_issues = (
        db.query(models.ValidationError)
        .filter(models.ValidationError.status.in_(ACTIVE_STATUSES))
        .all()
    )
    checks = db.query(models.ApiCheck).order_by(models.ApiCheck.checked_at.desc()).limit(80).all()
    healthy_checks = sum(1 for check in checks if check.check_status == "Healthy")

    trend_start = datetime.utcnow() - timedelta(days=13)
    trend_buckets = defaultdict(int)
    for issue in active_issues:
        if issue.created_at >= trend_start:
            trend_buckets[issue.created_at.date().isoformat()] += 1
    issue_trend = [
        {
            "date": (trend_start.date() + timedelta(days=offset)).isoformat(),
            "issues": trend_buckets[(trend_start.date() + timedelta(days=offset)).isoformat()],
        }
        for offset in range(14)
    ]

    return {
        "partner_count": len(partners),
        "open_blockers": len(active_issues),
        "average_readiness_score": round(sum(latest_scores) / len(latest_scores), 1) if latest_scores else 0,
        "api_health_pct": round(100 * healthy_checks / len(checks), 1) if checks else 0,
        "status_counts": Counter(partner.integration_status for partner in partners),
        "severity_counts": Counter(issue.severity for issue in active_issues),
        "category_counts": Counter(issue.category for issue in active_issues),
        "issue_trend": issue_trend,
        "top_recurring_failures": Counter(issue.rule_name for issue in active_issues).most_common(6),
        "partner_cards": [_partner_summary(db, partner) for partner in partners],
    }

