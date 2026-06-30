from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session, selectinload

from app import models
from app.services.validation import SUPPORTED_ARTWORK_TYPES


ACTIVE_STATUSES = {"Open", "In Review", "Partner Action Needed"}


def calculate_readiness(db: Session, partner_id: int, feed_id: int | None = None) -> models.ReadinessScore:
    feed = _target_feed(db, partner_id, feed_id)
    content_query = (
        db.query(models.ContentItem)
        .options(
            selectinload(models.ContentItem.artwork_assets),
            selectinload(models.ContentItem.entitlement_rules),
            selectinload(models.ContentItem.availability_windows),
        )
        .filter(models.ContentItem.partner_id == partner_id)
    )
    if feed:
        content_query = content_query.filter(models.ContentItem.feed_id == feed.feed_id)
    content_items = content_query.all()

    issue_query = db.query(models.ValidationError).filter(
        models.ValidationError.partner_id == partner_id,
        models.ValidationError.status.in_(ACTIVE_STATUSES),
    )
    if feed:
        issue_query = issue_query.filter(models.ValidationError.feed_id == feed.feed_id)
    issues = issue_query.all()

    critical_count = sum(1 for issue in issues if issue.severity == "Critical")
    high_count = sum(1 for issue in issues if issue.severity == "High")
    medium_count = sum(1 for issue in issues if issue.severity == "Medium")
    low_count = sum(1 for issue in issues if issue.severity == "Low")

    blocked_content_ids = {issue.content_id for issue in issues if issue.content_id and issue.severity in {"Critical", "High"}}
    total_content = len(content_items)
    valid_content_pct = 100.0 if total_content == 0 else 100 * (total_content - len(blocked_content_ids)) / total_content
    artwork_completion_pct = _artwork_completion(content_items)
    entitlement_completion_pct = _entitlement_completion(content_items)
    api_health_score = _api_health_score(db, partner_id)
    sla_penalty = _sla_penalty(issues)

    score = (
        100
        - critical_count * 10
        - high_count * 4
        - medium_count * 1.5
        - low_count * 0.5
        - sla_penalty
        + (valid_content_pct - 100) * 0.2
        + (artwork_completion_pct - 100) * 0.12
        + (entitlement_completion_pct - 100) * 0.12
        + (api_health_score - 100) * 0.15
    )
    score = round(max(0, min(100, score)), 1)

    readiness = models.ReadinessScore(
        partner_id=partner_id,
        feed_id=feed.feed_id if feed else feed_id,
        readiness_score=score,
        critical_count=critical_count,
        high_count=high_count,
        valid_content_pct=round(valid_content_pct, 1),
        artwork_completion_pct=round(artwork_completion_pct, 1),
        entitlement_completion_pct=round(entitlement_completion_pct, 1),
        api_health_score=round(api_health_score, 1),
    )
    db.add(readiness)

    partner = db.get(models.Partner, partner_id)
    if partner and partner.integration_status != "Live":
        if critical_count > 0:
            partner.integration_status = "Blocked"
        elif high_count > 0:
            partner.integration_status = "Testing"
        elif score >= 85:
            partner.integration_status = "Ready"
        elif total_content:
            partner.integration_status = "Testing"

    db.commit()
    db.refresh(readiness)
    return readiness


def _target_feed(db: Session, partner_id: int, feed_id: int | None) -> models.FeedUpload | None:
    if feed_id:
        return db.get(models.FeedUpload, feed_id)
    return (
        db.query(models.FeedUpload)
        .filter(models.FeedUpload.partner_id == partner_id)
        .order_by(models.FeedUpload.uploaded_at.desc())
        .first()
    )


def _artwork_completion(content_items: list[models.ContentItem]) -> float:
    if not content_items:
        return 0
    complete = 0
    for item in content_items:
        if any(
            asset.artwork_url
            and asset.width
            and asset.width >= 1280
            and asset.height
            and asset.height >= 720
            and (asset.file_type or "").lower().strip(".") in SUPPORTED_ARTWORK_TYPES
            for asset in item.artwork_assets
        ):
            complete += 1
    return 100 * complete / len(content_items)


def _entitlement_completion(content_items: list[models.ContentItem]) -> float:
    premium_items = [item for item in content_items if item.is_premium]
    if not premium_items:
        return 100.0
    complete = 0
    for item in premium_items:
        availability_packages = [window.entitlement_package for window in item.availability_windows if window.entitlement_package]
        if item.entitlement_rules or availability_packages:
            complete += 1
    return 100 * complete / len(premium_items)


def _api_health_score(db: Session, partner_id: int) -> float:
    checks = (
        db.query(models.ApiCheck)
        .filter(models.ApiCheck.partner_id == partner_id)
        .order_by(models.ApiCheck.checked_at.desc())
        .limit(10)
        .all()
    )
    if not checks:
        return 75.0
    successes = sum(1 for check in checks if check.check_status == "Healthy")
    latency_score = sum(max(0, 100 - (check.latency_ms / 20)) for check in checks) / len(checks)
    return (successes / len(checks)) * 70 + latency_score * 0.30


def _sla_penalty(issues: list[models.ValidationError]) -> float:
    now = datetime.utcnow()
    penalty = 0.0
    for issue in issues:
        age_days = max(0, (now - issue.created_at).days)
        if issue.severity == "Critical" and age_days > 2:
            penalty += min(10, age_days - 2)
        elif issue.severity == "High" and age_days > 5:
            penalty += min(5, (age_days - 5) * 0.5)
    return min(15, penalty)
