from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Partner(Base):
    __tablename__ = "partners"

    partner_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    partner_name: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    contact_email: Mapped[str] = mapped_column(String(180), nullable=False)
    integration_status: Mapped[str] = mapped_column(String(40), nullable=False, default="Draft")
    launch_target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    region_scope: Mapped[str] = mapped_column(String(120), nullable=False, default="US")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    feeds: Mapped[list["FeedUpload"]] = relationship(back_populates="partner", cascade="all, delete-orphan")
    content_items: Mapped[list["ContentItem"]] = relationship(back_populates="partner", cascade="all, delete-orphan")
    validation_errors: Mapped[list["ValidationError"]] = relationship(back_populates="partner", cascade="all, delete-orphan")
    api_checks: Mapped[list["ApiCheck"]] = relationship(back_populates="partner", cascade="all, delete-orphan")
    readiness_scores: Mapped[list["ReadinessScore"]] = relationship(back_populates="partner", cascade="all, delete-orphan")
    onboarding_tasks: Mapped[list["OnboardingTask"]] = relationship(back_populates="partner", cascade="all, delete-orphan")


class FeedUpload(Base):
    __tablename__ = "feed_uploads"

    feed_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.partner_id"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(220), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    parse_status: Mapped[str] = mapped_column(String(40), nullable=False, default="Pending")
    parser_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    partner: Mapped[Partner] = relationship(back_populates="feeds")
    content_items: Mapped[list["ContentItem"]] = relationship(back_populates="feed", cascade="all, delete-orphan")
    validation_errors: Mapped[list["ValidationError"]] = relationship(back_populates="feed", cascade="all, delete-orphan")
    readiness_scores: Mapped[list["ReadinessScore"]] = relationship(back_populates="feed", cascade="all, delete-orphan")


class ContentItem(Base):
    __tablename__ = "content_items"

    content_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.partner_id"), nullable=False, index=True)
    feed_id: Mapped[int] = mapped_column(ForeignKey("feed_uploads.feed_id"), nullable=False, index=True)
    partner_content_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    title: Mapped[str | None] = mapped_column(String(260), nullable=True)
    series_title: Mapped[str | None] = mapped_column(String(260), nullable=True)
    season_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    episode_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    asset_type: Mapped[str] = mapped_column(String(40), nullable=False, default="movie")
    channel_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    content_rating: Mapped[str | None] = mapped_column(String(40), nullable=True)
    playback_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    drm_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    partner: Mapped[Partner] = relationship(back_populates="content_items")
    feed: Mapped[FeedUpload] = relationship(back_populates="content_items")
    artwork_assets: Mapped[list["ArtworkAsset"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    availability_windows: Mapped[list["AvailabilityWindow"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    captions: Mapped[list["Caption"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    entitlement_rules: Mapped[list["EntitlementRule"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    validation_errors: Mapped[list["ValidationError"]] = relationship(back_populates="content")


class ArtworkAsset(Base):
    __tablename__ = "artwork_assets"

    artwork_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content_items.content_id"), nullable=False, index=True)
    artwork_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    validation_status: Mapped[str] = mapped_column(String(40), nullable=False, default="Pending")

    content: Mapped[ContentItem] = relationship(back_populates="artwork_assets")


class AvailabilityWindow(Base):
    __tablename__ = "availability_windows"

    availability_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content_items.content_id"), nullable=False, index=True)
    region: Mapped[str | None] = mapped_column(String(12), nullable=True, index=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    entitlement_package: Mapped[str | None] = mapped_column(String(120), nullable=True)

    content: Mapped[ContentItem] = relationship(back_populates="availability_windows")


class Caption(Base):
    __tablename__ = "captions"

    caption_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content_items.content_id"), nullable=False, index=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    region: Mapped[str | None] = mapped_column(String(12), nullable=True)
    caption_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    validation_status: Mapped[str] = mapped_column(String(40), nullable=False, default="Pending")

    content: Mapped[ContentItem] = relationship(back_populates="captions")


class EntitlementRule(Base):
    __tablename__ = "entitlement_rules"

    entitlement_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content_items.content_id"), nullable=False, index=True)
    package_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    package_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    region: Mapped[str | None] = mapped_column(String(12), nullable=True)
    entitlement_type: Mapped[str | None] = mapped_column(String(80), nullable=True)

    content: Mapped[ContentItem] = relationship(back_populates="entitlement_rules")


class ApiCheck(Base):
    __tablename__ = "api_checks"

    check_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.partner_id"), nullable=False, index=True)
    endpoint: Mapped[str] = mapped_column(String(260), nullable=False)
    http_status: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    check_status: Mapped[str] = mapped_column(String(40), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    partner: Mapped[Partner] = relationship(back_populates="api_checks")


class ValidationError(Base):
    __tablename__ = "validation_errors"

    error_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.partner_id"), nullable=False, index=True)
    feed_id: Mapped[int | None] = mapped_column(ForeignKey("feed_uploads.feed_id"), nullable=True, index=True)
    content_id: Mapped[int | None] = mapped_column(ForeignKey("content_items.content_id"), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(120), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_fix: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="Open")
    assigned_owner: Mapped[str] = mapped_column(String(120), nullable=False, default="Partner Engineering")
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    partner: Mapped[Partner] = relationship(back_populates="validation_errors")
    feed: Mapped[FeedUpload | None] = relationship(back_populates="validation_errors")
    content: Mapped[ContentItem | None] = relationship(back_populates="validation_errors")


class ReadinessScore(Base):
    __tablename__ = "readiness_scores"

    score_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.partner_id"), nullable=False, index=True)
    feed_id: Mapped[int | None] = mapped_column(ForeignKey("feed_uploads.feed_id"), nullable=True, index=True)
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    critical_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    high_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_content_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    artwork_completion_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    entitlement_completion_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    api_health_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    partner: Mapped[Partner] = relationship(back_populates="readiness_scores")
    feed: Mapped[FeedUpload | None] = relationship(back_populates="readiness_scores")


class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.partner_id"), nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(220), nullable=False)
    owner: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="Open")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    partner: Mapped[Partner] = relationship(back_populates="onboarding_tasks")
