from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

from app import models
from app.services.readiness import ACTIVE_STATUSES, calculate_readiness


def integration_checklist(db: Session, partner_id: int) -> dict:
    partner = db.get(models.Partner, partner_id)
    if not partner:
        raise ValueError(f"Partner {partner_id} was not found.")
    latest_score = (
        db.query(models.ReadinessScore)
        .filter(models.ReadinessScore.partner_id == partner_id)
        .order_by(models.ReadinessScore.generated_at.desc())
        .first()
    ) or calculate_readiness(db, partner_id)
    open_issues = (
        db.query(models.ValidationError)
        .filter(models.ValidationError.partner_id == partner_id, models.ValidationError.status.in_(ACTIVE_STATUSES))
        .all()
    )
    critical = [issue for issue in open_issues if issue.severity == "Critical"]
    high = [issue for issue in open_issues if issue.severity == "High"]

    return {
        "partner": partner.partner_name,
        "launch_status": partner.integration_status,
        "readiness_score": latest_score.readiness_score,
        "required_before_go_live": [
            "Resolve all critical and high validation blockers.",
            "Confirm artwork meets 1280x720 minimum dimensions.",
            "Verify premium content has matching entitlement packages and DRM.",
            "Run API checks with successful metadata, playback, captions, and entitlement responses.",
            "Re-upload and validate final launch candidate feed.",
        ],
        "current_blockers": {
            "critical": len(critical),
            "high": len(high),
            "top_rules": Counter(issue.rule_name for issue in open_issues).most_common(5),
        },
        "metrics": {
            "valid_content_pct": latest_score.valid_content_pct,
            "artwork_completion_pct": latest_score.artwork_completion_pct,
            "entitlement_completion_pct": latest_score.entitlement_completion_pct,
            "api_health_score": latest_score.api_health_score,
        },
    }


def troubleshooting_summary(db: Session, partner_id: int) -> dict:
    partner = db.get(models.Partner, partner_id)
    if not partner:
        raise ValueError(f"Partner {partner_id} was not found.")
    issues = (
        db.query(models.ValidationError)
        .filter(models.ValidationError.partner_id == partner_id, models.ValidationError.status.in_(ACTIVE_STATUSES))
        .all()
    )
    by_rule = Counter(issue.rule_name for issue in issues)
    by_category = Counter(issue.category for issue in issues)
    critical = sum(1 for issue in issues if issue.severity == "Critical")
    high = sum(1 for issue in issues if issue.severity == "High")
    top_rules = by_rule.most_common(3)

    if not issues:
        summary = (
            f"{partner.partner_name} is ready for launch validation. No open feed or API blockers are currently active."
        )
    else:
        blockers = ", ".join(f"{count} {rule.replace('_', ' ')}" for rule, count in top_rules)
        summary = (
            f"{partner.partner_name} is not ready for launch. The main blockers are {blockers}. "
            "Recommended next steps: resolve critical validation errors, re-run API checks, and revalidate the launch feed."
        )

    return {
        "partner": partner.partner_name,
        "summary": summary,
        "critical_count": critical,
        "high_count": high,
        "top_categories": by_category.most_common(5),
        "next_actions": [
            "Fix critical playback, entitlement, and availability blockers first.",
            "Ask the partner to re-upload a corrected feed in the sandbox.",
            "Use the API troubleshooting page to replay failed integration checks.",
        ],
    }


def product_feedback_report(db: Session) -> dict:
    issues = db.query(models.ValidationError).all()
    checks = db.query(models.ApiCheck).all()
    partner_names = {
        partner.partner_id: partner.partner_name for partner in db.query(models.Partner).all()
    }
    repeated = Counter(issue.partner_id for issue in issues if issue.severity in {"Critical", "High"})
    api_failures = Counter(check.error_message or "Healthy" for check in checks if check.check_status != "Healthy")
    validation_failures = Counter(issue.rule_name for issue in issues)

    return {
        "top_validation_failures": validation_failures.most_common(8),
        "top_api_failures": api_failures.most_common(6),
        "partners_with_repeated_blockers": [
            {"partner": partner_names.get(partner_id, f"Partner {partner_id}"), "blockers": count}
            for partner_id, count in repeated.most_common(8)
        ],
        "suggested_self_service_features": [
            "Pre-upload artwork dimension checker",
            "Region/package compatibility preview",
            "Inline duplicate content ID detection",
            "Partner API contract test harness",
        ],
        "recommended_product_improvements": [
            "Add schema-specific validation templates for premium, sports, kids, and live news partners.",
            "Expose SLA aging alerts to partner managers before launch dates slip.",
            "Create reusable API failure playbooks for authentication, throttling, and timeout errors.",
        ],
    }
