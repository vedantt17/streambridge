from pathlib import Path

from app.services.parser import parse_feed_file


SAMPLES = Path(__file__).resolve().parents[2] / "sample-feeds"


def test_parse_json_feed_normalizes_records():
    parsed = parse_feed_file(SAMPLES / "northstar-sports-sample.json", "json")

    assert parsed.errors == []
    assert len(parsed.records) == 2
    assert parsed.records[0]["partner_content_id"] == "NSN-1001"
    assert parsed.records[0]["artwork"][0]["width"] == 1920
    assert parsed.records[1]["is_premium"] is True


def test_parse_xml_feed_normalizes_nested_records():
    parsed = parse_feed_file(SAMPLES / "cinewave-premium-sample.xml", "xml")

    assert parsed.errors == []
    assert len(parsed.records) == 2
    assert parsed.records[0]["partner_content_id"] == "CWP-2001"
    assert parsed.records[0]["entitlements"][0]["package_id"] == "PREMIUM-MOVIES"


def test_parse_csv_feed_normalizes_flat_columns():
    parsed = parse_feed_file(SAMPLES / "metrostream-sample.csv", "csv")

    assert parsed.errors == []
    assert len(parsed.records) == 3
    assert parsed.records[1]["availability"][0]["entitlement_package"] == "METRO-PREMIUM"

