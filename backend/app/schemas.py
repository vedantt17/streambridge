from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PartnerCreate(BaseModel):
    partner_name: str = Field(min_length=2, max_length=160)
    contact_email: EmailStr
    integration_status: str = "Draft"
    launch_target_date: date | None = None
    region_scope: str = "US"


class PartnerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    partner_id: int
    partner_name: str
    contact_email: str
    integration_status: str
    launch_target_date: date | None
    region_scope: str
    created_at: datetime


class FeedUploadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feed_id: int
    partner_id: int
    file_name: str
    file_type: str
    uploaded_at: datetime
    parse_status: str
    parser_error: str | None = None


class IssuePatch(BaseModel):
    status: str | None = None
    assigned_owner: str | None = None
    resolution_notes: str | None = None


class ValidationErrorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    error_id: int
    partner_id: int
    feed_id: int | None
    content_id: int | None
    severity: str
    category: str
    rule_name: str
    error_message: str
    recommended_fix: str
    status: str
    assigned_owner: str
    resolution_notes: str | None
    created_at: datetime
    resolved_at: datetime | None


class ApiCheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    check_id: int
    partner_id: int
    endpoint: str
    http_status: int
    latency_ms: int
    check_status: str
    checked_at: datetime
    error_message: str | None


class ReadinessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score_id: int
    partner_id: int
    feed_id: int | None
    readiness_score: float
    critical_count: int
    high_count: int
    valid_content_pct: float
    artwork_completion_pct: float
    entitlement_completion_pct: float
    api_health_score: float
    generated_at: datetime


class ParseResult(BaseModel):
    feed_id: int
    parse_status: str
    content_records: int
    parser_error: str | None = None


class ValidationResult(BaseModel):
    feed_id: int
    issue_count: int
    severity_counts: dict[str, int]
    readiness: dict[str, Any]
