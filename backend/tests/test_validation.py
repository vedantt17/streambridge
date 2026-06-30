from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services.validation import validate_feed


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


def test_validation_flags_launch_blockers(db_session):
    partner = models.Partner(partner_name="Test Partner", contact_email="ops@example.test")
    db_session.add(partner)
    db_session.flush()
    feed = models.FeedUpload(
        partner_id=partner.partner_id,
        file_name="bad.json",
        file_type="json",
        raw_file_path="/tmp/bad.json",
        parse_status="Parsed",
    )
    db_session.add(feed)
    db_session.flush()
    content = models.ContentItem(
        partner_id=partner.partner_id,
        feed_id=feed.feed_id,
        partner_content_id="DUP-1",
        title="",
        asset_type="episode",
        channel_id=None,
        language=None,
        content_rating=None,
        playback_url="not-a-url",
        drm_required=False,
        is_premium=True,
    )
    db_session.add(content)
    db_session.flush()
    db_session.add(
        models.AvailabilityWindow(
            content_id=content.content_id,
            region="ZZ",
            start_date=date(2026, 8, 1),
            end_date=date(2026, 7, 1),
        )
    )
    db_session.add(models.ArtworkAsset(content_id=content.content_id, artwork_url="", width=640, height=360, file_type="bmp"))
    db_session.commit()

    errors = validate_feed(db_session, feed.feed_id)
    rules = {error.rule_name for error in errors}

    assert "missing_title" in rules
    assert "invalid_series_season_episode_hierarchy" in rules
    assert "end_date_before_start_date" in rules
    assert "unsupported_region_code" in rules
    assert "invalid_playback_url_format" in rules
    assert "drm_required_but_missing" in rules

