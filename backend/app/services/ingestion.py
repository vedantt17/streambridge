from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app import models


def store_parsed_records(db: Session, feed: models.FeedUpload, records: list[dict[str, Any]]) -> int:
    for existing in list(feed.content_items):
        db.delete(existing)
    db.query(models.ValidationError).filter(models.ValidationError.feed_id == feed.feed_id).delete(
        synchronize_session=False
    )
    db.flush()

    for record in records:
        content = models.ContentItem(
            partner_id=feed.partner_id,
            feed_id=feed.feed_id,
            partner_content_id=_string(record.get("partner_content_id")),
            title=_string(record.get("title")),
            series_title=_string(record.get("series_title")),
            season_number=_int(record.get("season_number")),
            episode_number=_int(record.get("episode_number")),
            asset_type=_string(record.get("asset_type")) or "movie",
            channel_id=_string(record.get("channel_id")),
            language=_string(record.get("language")),
            content_rating=_string(record.get("content_rating")),
            playback_url=_string(record.get("playback_url")),
            drm_required=_bool(record.get("drm_required")),
            is_premium=_bool(record.get("is_premium")),
        )
        db.add(content)
        db.flush()

        for artwork in record.get("artwork", []):
            db.add(
                models.ArtworkAsset(
                    content_id=content.content_id,
                    artwork_url=_string(artwork.get("artwork_url") or artwork.get("url") or artwork.get("value")),
                    width=_int(artwork.get("width")),
                    height=_int(artwork.get("height")),
                    file_type=_string(artwork.get("file_type") or artwork.get("type")),
                )
            )
        for window in record.get("availability", []):
            db.add(
                models.AvailabilityWindow(
                    content_id=content.content_id,
                    region=_string(window.get("region")),
                    start_date=_date(window.get("start_date")),
                    end_date=_date(window.get("end_date")),
                    entitlement_package=_string(window.get("entitlement_package") or window.get("package")),
                )
            )
        for caption in record.get("captions", []):
            db.add(
                models.Caption(
                    content_id=content.content_id,
                    language=_string(caption.get("language")),
                    region=_string(caption.get("region")),
                    caption_url=_string(caption.get("caption_url") or caption.get("url") or caption.get("value")),
                )
            )
        for entitlement in record.get("entitlements", []):
            db.add(
                models.EntitlementRule(
                    content_id=content.content_id,
                    package_id=_string(entitlement.get("package_id") or entitlement.get("id")),
                    package_name=_string(entitlement.get("package_name") or entitlement.get("name")),
                    region=_string(entitlement.get("region")),
                    entitlement_type=_string(entitlement.get("entitlement_type") or entitlement.get("type")),
                )
            )

    feed.parse_status = "Parsed"
    feed.parser_error = None
    db.commit()
    db.refresh(feed)
    return len(records)


def _string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y", "premium"}


def _date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if value in (None, ""):
        return None
    text = str(value).strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None
