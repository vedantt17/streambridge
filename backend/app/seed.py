from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine
from app.services.readiness import calculate_readiness


PARTNER_NAMES = [
    "Northstar Sports Network",
    "MetroStream Channels",
    "CineWave Premium",
    "Horizon Kids TV",
    "Global News Live",
    "Vista Entertainment",
    "Summit Deportes",
    "Pulse Reality Network",
]

RULES = [
    ("Critical", "Playback", "missing_playback_url", "Playback URL is missing.", "Provide a playable HLS/DASH URL."),
    ("Critical", "Entitlement", "entitlement_package_missing", "Premium title has no entitlement package.", "Attach package IDs before launch."),
    ("High", "Artwork", "missing_artwork", "Artwork is missing.", "Provide 16:9 key art."),
    ("High", "Availability", "end_date_before_start_date", "Availability end date precedes start date.", "Correct the end date."),
    ("High", "Metadata", "duplicate_partner_content_id", "Duplicate partner content ID found.", "Deduplicate IDs in the feed."),
    ("Medium", "Captions", "missing_required_captions", "Required captions are missing.", "Attach captions for required regions."),
    ("Medium", "Artwork", "invalid_artwork_dimensions", "Artwork dimensions are below minimum.", "Upload 1280x720 or larger artwork."),
    ("Low", "API", "api_latency_warning", "Partner endpoint latency is elevated.", "Review partner API performance."),
]


def seed_if_empty(db: Session) -> None:
    if db.query(models.Partner).count() > 0:
        return
    seed_database(db)


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_database(db: Session) -> None:
    rng = random.Random(42)
    today = date.today()
    storage_dir = Path(__file__).resolve().parents[1] / "storage" / "uploads"
    storage_dir.mkdir(parents=True, exist_ok=True)

    partners: list[models.Partner] = []
    statuses = ["Testing", "Blocked", "Ready", "Testing", "Live", "Blocked", "Testing", "Draft"]
    region_scopes = ["US,CA", "US,MX", "US,CA,GB", "US", "US,GB,DE", "US,BR", "US,MX,ES", "US,CA"]
    for idx, name in enumerate(PARTNER_NAMES):
        partner = models.Partner(
            partner_name=name,
            contact_email=f"partner-ops-{idx + 1}@examplemedia.test",
            integration_status=statuses[idx],
            launch_target_date=today + timedelta(days=14 + idx * 6),
            region_scope=region_scopes[idx],
            created_at=datetime.utcnow() - timedelta(days=35 - idx),
        )
        db.add(partner)
        partners.append(partner)
    db.flush()

    feeds: list[models.FeedUpload] = []
    feed_types = ["json", "xml", "csv"]
    for idx in range(25):
        partner = partners[idx % len(partners)]
        feed_type = feed_types[idx % len(feed_types)]
        feed = models.FeedUpload(
            partner_id=partner.partner_id,
            file_name=f"{partner.partner_name.lower().replace(' ', '_')}_launch_{idx + 1}.{feed_type}",
            file_type=feed_type,
            raw_file_path=str(storage_dir / f"seed_feed_{idx + 1}.{feed_type}"),
            uploaded_at=datetime.utcnow() - timedelta(days=rng.randint(0, 25), hours=rng.randint(0, 18)),
            parse_status=rng.choice(["Parsed", "Parsed", "Parsed", "Failed"]),
            parser_error=None,
        )
        if feed.parse_status == "Failed":
            feed.parser_error = "Malformed sample row near artwork_assets[3]."
        db.add(feed)
        feeds.append(feed)
    db.flush()

    content_items: list[models.ContentItem] = []
    asset_types = ["movie", "episode", "live", "sports", "news"]
    languages = ["en", "es", "fr", "de", "pt", "hi"]
    ratings = ["TV-G", "TV-PG", "TV-14", "TV-MA", "PG", "R"]
    for idx in range(400):
        feed = feeds[idx % len(feeds)]
        is_episode = idx % 5 == 0
        content = models.ContentItem(
            partner_id=feed.partner_id,
            feed_id=feed.feed_id,
            partner_content_id=f"{PARTNER_NAMES[feed.partner_id - 1][:3].upper()}-{idx + 10000}",
            title=f"{rng.choice(['Prime', 'Weekend', 'Late Night', 'Global', 'Studio'])} Title {idx + 1}",
            series_title=f"Series {idx // 8}" if is_episode else None,
            season_number=(idx % 6) + 1 if is_episode else None,
            episode_number=(idx % 12) + 1 if is_episode else None,
            asset_type="episode" if is_episode else rng.choice(asset_types),
            channel_id=f"CH-{feed.partner_id:02d}",
            language=rng.choice(languages),
            content_rating=rng.choice(ratings),
            playback_url=f"https://stream.example.test/{feed.partner_id}/{idx}/master.m3u8",
            drm_required=idx % 4 == 0,
            is_premium=idx % 4 == 0 or feed.partner_id in {3, 6},
            created_at=datetime.utcnow() - timedelta(days=rng.randint(0, 30)),
        )
        db.add(content)
        content_items.append(content)
    db.flush()

    for idx, content in enumerate(content_items[:150]):
        db.add(
            models.ArtworkAsset(
                content_id=content.content_id,
                artwork_url=f"https://cdn.example.test/art/{content.partner_content_id}.jpg",
                width=1920 if idx % 7 else 960,
                height=1080 if idx % 7 else 540,
                file_type="jpg" if idx % 11 else "bmp",
                validation_status="Valid" if idx % 7 and idx % 11 else "Needs Fix",
            )
        )

    regions = ["US", "CA", "MX", "GB", "DE", "BR", "ES", "JP", "IN"]
    for idx, content in enumerate(content_items[:300]):
        start = today - timedelta(days=rng.randint(0, 20))
        db.add(
            models.AvailabilityWindow(
                content_id=content.content_id,
                region=rng.choice(regions),
                start_date=start,
                end_date=start + timedelta(days=rng.randint(14, 180)),
                entitlement_package=f"PKG-{content.partner_id}-{idx % 6}" if content.is_premium else None,
            )
        )

    for idx, content in enumerate(content_items[:100]):
        db.add(
            models.Caption(
                content_id=content.content_id,
                language=content.language or "en",
                region=rng.choice(["US", "CA", "GB"]),
                caption_url=f"https://cdn.example.test/captions/{content.partner_content_id}.vtt",
                validation_status="Valid",
            )
        )

    premium_items = [item for item in content_items if item.is_premium]
    for idx, content in enumerate(premium_items[:80]):
        db.add(
            models.EntitlementRule(
                content_id=content.content_id,
                package_id=f"PKG-{content.partner_id}-{idx % 6}",
                package_name=rng.choice(["Sports Plus", "Premium Movies", "Family Pack", "Global News"]),
                region=rng.choice(["US", "CA", "GB", "MX"]),
                entitlement_type=rng.choice(["SVOD", "TVOD", "Linear Add-on"]),
            )
        )

    owners = ["Partner Engineering", "Partner Operations", "Content Ops", "Playback Engineering", "Accessibility Ops"]
    statuses = ["Open", "Open", "In Review", "Partner Action Needed", "Resolved"]
    for idx in range(200):
        content = rng.choice(content_items)
        severity, category, rule, message, fix = rng.choice(RULES)
        created_at = datetime.utcnow() - timedelta(days=rng.randint(0, 24), hours=rng.randint(0, 23))
        status = rng.choice(statuses)
        db.add(
            models.ValidationError(
                partner_id=content.partner_id,
                feed_id=content.feed_id,
                content_id=content.content_id,
                severity=severity,
                category=category,
                rule_name=rule,
                error_message=f"Content {content.partner_content_id}: {message}",
                recommended_fix=fix,
                status=status,
                assigned_owner=rng.choice(owners),
                resolution_notes="Validated with partner on latest feed." if status == "Resolved" else None,
                created_at=created_at,
                resolved_at=created_at + timedelta(days=2) if status == "Resolved" else None,
            )
        )

    endpoints = ["/metadata/v1/feed", "/availability/v1/windows", "/playback/v1/manifest", "/entitlements/v1/packages"]
    for idx in range(60):
        partner = partners[idx % len(partners)]
        healthy = rng.random() > 0.25
        db.add(
            models.ApiCheck(
                partner_id=partner.partner_id,
                endpoint=rng.choice(endpoints),
                http_status=200 if healthy else rng.choice([401, 409, 429, 500, 504]),
                latency_ms=rng.randint(90, 900 if healthy else 4600),
                check_status="Healthy" if healthy else "Failed",
                checked_at=datetime.utcnow() - timedelta(days=rng.randint(0, 10), hours=rng.randint(0, 18)),
                error_message=None if healthy else rng.choice(["Timeout", "Auth token rejected", "Rate limit exceeded"]),
            )
        )

    task_names = [
        "Validate partner feed schema",
        "Confirm entitlement package mapping",
        "Review artwork requirements",
        "Run playback API check",
        "Prepare launch readiness sign-off",
    ]
    for partner in partners:
        for offset, task_name in enumerate(task_names):
            db.add(
                models.OnboardingTask(
                    partner_id=partner.partner_id,
                    task_name=task_name,
                    owner=rng.choice(owners),
                    status=rng.choice(["Open", "In Review", "Done", "Partner Action Needed"]),
                    due_date=today + timedelta(days=offset * 3 + rng.randint(1, 12)),
                    completed_at=datetime.utcnow() - timedelta(days=rng.randint(0, 4)) if rng.random() > 0.72 else None,
                )
            )

    db.commit()
    for partner in partners:
        calculate_readiness(db, partner.partner_id)


if __name__ == "__main__":
    from app.database import SessionLocal, init_db

    reset_database()
    init_db()
    with SessionLocal() as session:
        seed_database(session)
    print("Seeded StreamBridge database.")

