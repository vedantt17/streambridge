from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from urllib.parse import urlparse

from sqlalchemy.orm import Session, selectinload

from app import models


SUPPORTED_REGIONS = {"US", "CA", "MX", "GB", "DE", "FR", "ES", "BR", "IN", "JP"}
REQUIRED_CAPTION_REGIONS = {"US", "CA", "GB"}
SUPPORTED_ARTWORK_TYPES = {"jpg", "jpeg", "png", "webp"}


@dataclass
class RuleFinding:
    severity: str
    category: str
    rule_name: str
    error_message: str
    recommended_fix: str
    content_id: int | None = None


def validate_feed(db: Session, feed_id: int) -> list[models.ValidationError]:
    feed = db.get(models.FeedUpload, feed_id)
    if not feed:
        raise ValueError(f"Feed {feed_id} was not found.")

    db.query(models.ValidationError).filter(models.ValidationError.feed_id == feed_id).delete(
        synchronize_session=False
    )
    db.flush()

    content_items = (
        db.query(models.ContentItem)
        .options(
            selectinload(models.ContentItem.artwork_assets),
            selectinload(models.ContentItem.availability_windows),
            selectinload(models.ContentItem.captions),
            selectinload(models.ContentItem.entitlement_rules),
        )
        .filter(models.ContentItem.feed_id == feed_id)
        .all()
    )

    findings: list[RuleFinding] = []
    if feed.file_type.lower() not in {"json", "xml", "csv"}:
        findings.append(
            RuleFinding(
                "Critical",
                "Metadata",
                "unsupported_metadata_format",
                f"{feed.file_type} is not a supported partner feed format.",
                "Submit a JSON, XML, or CSV feed that matches the integration guide.",
            )
        )
    if feed.parse_status != "Parsed":
        findings.append(
            RuleFinding(
                "Critical",
                "Metadata",
                "parser_error",
                feed.parser_error or "Feed has not been parsed successfully.",
                "Fix feed syntax or upload a valid sample before validation.",
            )
        )

    partner_ids = [item.partner_content_id for item in content_items if item.partner_content_id]
    duplicate_ids = {content_id for content_id, count in Counter(partner_ids).items() if count > 1}

    for item in content_items:
        findings.extend(_validate_content_item(item, duplicate_ids))

    db_errors = [
        models.ValidationError(
            partner_id=feed.partner_id,
            feed_id=feed.feed_id,
            content_id=finding.content_id,
            severity=finding.severity,
            category=finding.category,
            rule_name=finding.rule_name,
            error_message=finding.error_message,
            recommended_fix=finding.recommended_fix,
            status="Open",
            assigned_owner=_owner_for_category(finding.category),
        )
        for finding in findings
    ]
    db.add_all(db_errors)
    db.commit()
    return db_errors


def _validate_content_item(item: models.ContentItem, duplicate_ids: set[str]) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    prefix = f"Content {item.partner_content_id or item.content_id}: "

    def add(severity: str, category: str, rule: str, message: str, fix: str) -> None:
        findings.append(RuleFinding(severity, category, rule, prefix + message, fix, item.content_id))

    if not item.title:
        add("High", "Metadata", "missing_title", "title is missing.", "Provide a localized title for every asset.")
    if not item.partner_content_id:
        add(
            "Critical",
            "Metadata",
            "missing_content_id",
            "partner content ID is missing.",
            "Add a stable partner_content_id that will not change between feed deliveries.",
        )
    elif item.partner_content_id in duplicate_ids:
        add(
            "High",
            "Metadata",
            "duplicate_partner_content_id",
            "partner content ID appears more than once in the feed.",
            "Deduplicate partner_content_id values before revalidating.",
        )
    if item.asset_type.lower() == "episode" and (
        not item.series_title or item.season_number is None or item.episode_number is None
    ):
        add(
            "High",
            "Metadata",
            "invalid_series_season_episode_hierarchy",
            "episode assets require series title, season number, and episode number.",
            "Populate series_title, season_number, and episode_number for episodic content.",
        )
    if not item.channel_id:
        add("High", "Metadata", "missing_channel_id", "channel ID is missing.", "Map the asset to a valid channel_id.")
    if not item.language:
        add("Medium", "Metadata", "missing_language", "language is missing.", "Provide an ISO language code.")
    if not item.content_rating:
        add(
            "Medium",
            "Metadata",
            "missing_content_rating",
            "content rating is missing.",
            "Provide the required regional content rating.",
        )

    if not item.availability_windows:
        add(
            "Critical",
            "Availability",
            "invalid_availability_window",
            "availability window is missing.",
            "Add at least one start/end availability window.",
        )
    for window in item.availability_windows:
        if not window.start_date or not window.end_date:
            add(
                "High",
                "Availability",
                "invalid_availability_dates",
                f"availability dates are incomplete for region {window.region or 'unknown'}.",
                "Use ISO-8601 dates for start_date and end_date.",
            )
        elif window.end_date < window.start_date:
            add(
                "Critical",
                "Availability",
                "end_date_before_start_date",
                f"end date is before start date for region {window.region or 'unknown'}.",
                "Set end_date after start_date.",
            )
        if not window.region or window.region.upper() not in SUPPORTED_REGIONS:
            add(
                "High",
                "Availability",
                "unsupported_region_code",
                f"region {window.region or 'missing'} is unsupported.",
                f"Use one of: {', '.join(sorted(SUPPORTED_REGIONS))}.",
            )

    required_caption_regions = {
        window.region.upper()
        for window in item.availability_windows
        if window.region and window.region.upper() in REQUIRED_CAPTION_REGIONS
    }
    caption_regions = {caption.region.upper() for caption in item.captions if caption.region}
    missing_caption_regions = required_caption_regions - caption_regions
    if missing_caption_regions:
        add(
            "High",
            "Captions",
            "missing_required_captions",
            f"captions are missing for required regions {', '.join(sorted(missing_caption_regions))}.",
            "Attach caption/subtitle files for every required region.",
        )

    if not item.artwork_assets:
        add("High", "Artwork", "missing_artwork", "artwork is missing.", "Provide at least one 16:9 key art asset.")
    for artwork in item.artwork_assets:
        file_type = (artwork.file_type or "").lower().strip(".")
        if not artwork.artwork_url:
            add("Medium", "Artwork", "missing_artwork_url", "artwork URL is missing.", "Provide a reachable artwork URL.")
        if not artwork.width or not artwork.height or artwork.width < 1280 or artwork.height < 720:
            add(
                "Medium",
                "Artwork",
                "invalid_artwork_dimensions",
                "artwork dimensions are below the 1280x720 minimum.",
                "Upload artwork at 1280x720 or larger.",
            )
        if not file_type or file_type not in SUPPORTED_ARTWORK_TYPES:
            add(
                "Medium",
                "Artwork",
                "unsupported_artwork_file_type",
                f"artwork file type {artwork.file_type or 'missing'} is unsupported.",
                "Use jpg, jpeg, png, or webp artwork.",
            )

    if not item.playback_url:
        add("Critical", "Playback", "missing_playback_url", "playback URL is missing.", "Provide a playable HLS/DASH URL.")
    elif not _is_valid_url(item.playback_url):
        add(
            "Critical",
            "Playback",
            "invalid_playback_url_format",
            "playback URL is not a valid HTTP(S) URL.",
            "Use a fully qualified https:// or http:// playback URL.",
        )

    availability_packages = {window.entitlement_package for window in item.availability_windows if window.entitlement_package}
    entitlement_regions = {rule.region.upper() for rule in item.entitlement_rules if rule.region}
    availability_regions = {window.region.upper() for window in item.availability_windows if window.region}

    if item.is_premium and not item.drm_required:
        add(
            "Critical",
            "Entitlement",
            "drm_required_but_missing",
            "premium content is not marked as DRM required.",
            "Set drm_required=true for premium assets.",
        )
    if item.is_premium and not item.entitlement_rules and not availability_packages:
        add(
            "Critical",
            "Entitlement",
            "entitlement_package_missing",
            "premium content has no entitlement package.",
            "Attach package IDs or availability entitlement_package values.",
        )
    if item.entitlement_rules and availability_regions and not entitlement_regions.intersection(availability_regions):
        add(
            "High",
            "Entitlement",
            "package_region_mismatch",
            "entitlement regions do not match availability regions.",
            "Align entitlement regions with availability regions.",
        )

    return findings


def _is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _owner_for_category(category: str) -> str:
    return {
        "Metadata": "Partner Operations",
        "Artwork": "Content Ops",
        "Availability": "Partner Engineering",
        "Entitlement": "Partner Engineering",
        "Captions": "Accessibility Ops",
        "Playback": "Playback Engineering",
        "API": "Integration Engineering",
    }.get(category, "Partner Engineering")

