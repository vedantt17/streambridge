from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services.readiness import calculate_readiness


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def test_readiness_score_reflects_blockers_and_health(db_session):
    partner = models.Partner(partner_name="Readiness Partner", contact_email="ready@example.test")
    db_session.add(partner)
    db_session.flush()
    feed = models.FeedUpload(
        partner_id=partner.partner_id,
        file_name="feed.json",
        file_type="json",
        raw_file_path="/tmp/feed.json",
        parse_status="Parsed",
    )
    db_session.add(feed)
    db_session.flush()
    content = models.ContentItem(
        partner_id=partner.partner_id,
        feed_id=feed.feed_id,
        partner_content_id="READY-1",
        title="Ready Asset",
        channel_id="READY",
        language="en",
        content_rating="TV-PG",
        playback_url="https://example.test/master.m3u8",
        drm_required=True,
        is_premium=True,
    )
    db_session.add(content)
    db_session.flush()
    db_session.add(models.ArtworkAsset(content_id=content.content_id, artwork_url="https://cdn.test/a.jpg", width=1920, height=1080, file_type="jpg"))
    db_session.add(models.EntitlementRule(content_id=content.content_id, package_id="PKG", package_name="Premium", region="US", entitlement_type="SVOD"))
    db_session.add(models.ApiCheck(partner_id=partner.partner_id, endpoint="/metadata", http_status=200, latency_ms=120, check_status="Healthy"))
    db_session.add(
        models.ValidationError(
            partner_id=partner.partner_id,
            feed_id=feed.feed_id,
            content_id=content.content_id,
            severity="High",
            category="Artwork",
            rule_name="missing_artwork",
            error_message="Missing artwork.",
            recommended_fix="Add artwork.",
            status="Open",
            created_at=datetime.utcnow() - timedelta(days=1),
        )
    )
    db_session.commit()

    score = calculate_readiness(db_session, partner.partner_id, feed.feed_id)

    assert score.high_count == 1
    assert 0 < score.readiness_score < 100
    assert score.artwork_completion_pct == 100
    assert partner.integration_status == "Testing"

