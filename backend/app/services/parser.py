from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import pandas as pd


SUPPORTED_FEED_TYPES = {"json", "xml", "csv"}


@dataclass
class ParsedFeed:
    records: list[dict[str, Any]]
    errors: list[str]


def parse_feed_file(path: str | Path, file_type: str) -> ParsedFeed:
    normalized_type = file_type.lower().strip(".")
    feed_path = Path(path)
    if normalized_type not in SUPPORTED_FEED_TYPES:
        return ParsedFeed([], [f"Unsupported metadata format: {file_type}"])
    if not feed_path.exists():
        return ParsedFeed([], [f"Feed file not found: {feed_path}"])

    try:
        if normalized_type == "json":
            return _parse_json(feed_path)
        if normalized_type == "xml":
            return _parse_xml(feed_path)
        return _parse_csv(feed_path)
    except Exception as exc:  # Parser errors are stored for partner-facing triage.
        return ParsedFeed([], [str(exc)])


def _parse_json(path: Path) -> ParsedFeed:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("items") or data.get("content") or data.get("content_items") or []
    else:
        return ParsedFeed([], ["JSON feed must be an object or list."])

    if not isinstance(items, list):
        return ParsedFeed([], ["JSON feed items must be a list."])
    return ParsedFeed([normalize_record(item) for item in items], [])


def _parse_csv(path: Path) -> ParsedFeed:
    frame = pd.read_csv(path).fillna("")
    records = [normalize_record(row.to_dict()) for _, row in frame.iterrows()]
    return ParsedFeed(records, [])


def _parse_xml(path: Path) -> ParsedFeed:
    tree = ElementTree.parse(path)
    root = tree.getroot()
    nodes = root.findall(".//item") or root.findall(".//content_item") or root.findall(".//content")
    if not nodes and list(root):
        nodes = list(root)
    if not nodes and root.tag in {"item", "content_item", "content"}:
        nodes = [root]
    records = [normalize_record(_element_to_dict(node)) for node in nodes]
    return ParsedFeed(records, [])


def normalize_record(item: dict[str, Any]) -> dict[str, Any]:
    item = {str(key): value for key, value in item.items()}
    artwork = _listify(item.get("artwork") or item.get("artwork_assets") or item.get("artworks"))
    availability = _listify(item.get("availability") or item.get("availability_windows") or item.get("windows"))
    captions = _listify(item.get("captions") or item.get("subtitles"))
    entitlements = _listify(item.get("entitlements") or item.get("entitlement_rules"))

    if not artwork and any(item.get(key) not in (None, "") for key in ("artwork_url", "width", "height", "file_type")):
        artwork = [
            {
                "artwork_url": item.get("artwork_url"),
                "width": item.get("width") or item.get("artwork_width"),
                "height": item.get("height") or item.get("artwork_height"),
                "file_type": item.get("file_type") or item.get("artwork_file_type"),
            }
        ]
    if not availability and any(
        item.get(key) not in (None, "")
        for key in ("region", "availability_region", "start_date", "end_date", "entitlement_package")
    ):
        availability = [
            {
                "region": item.get("availability_region") or item.get("region"),
                "start_date": item.get("start_date") or item.get("availability_start"),
                "end_date": item.get("end_date") or item.get("availability_end"),
                "entitlement_package": item.get("entitlement_package"),
            }
        ]
    if not captions and any(item.get(key) not in (None, "") for key in ("caption_url", "caption_language", "caption_region")):
        captions = [
            {
                "language": item.get("caption_language") or item.get("language"),
                "region": item.get("caption_region") or item.get("region"),
                "caption_url": item.get("caption_url"),
            }
        ]
    if not entitlements and any(item.get(key) not in (None, "") for key in ("package_id", "package_name", "entitlement_region")):
        entitlements = [
            {
                "package_id": item.get("package_id"),
                "package_name": item.get("package_name"),
                "region": item.get("entitlement_region") or item.get("region"),
                "entitlement_type": item.get("entitlement_type") or "SVOD",
            }
        ]

    return {
        "partner_content_id": _string(item.get("partner_content_id") or item.get("content_id") or item.get("id")),
        "title": _string(item.get("title")),
        "series_title": _string(item.get("series_title")),
        "season_number": item.get("season_number"),
        "episode_number": item.get("episode_number"),
        "asset_type": _string(item.get("asset_type") or item.get("type") or "movie") or "movie",
        "channel_id": _string(item.get("channel_id")),
        "language": _string(item.get("language")),
        "content_rating": _string(item.get("content_rating") or item.get("rating")),
        "playback_url": _string(item.get("playback_url")),
        "drm_required": item.get("drm_required"),
        "is_premium": item.get("is_premium") or item.get("premium"),
        "artwork": artwork,
        "availability": availability,
        "captions": captions,
        "entitlements": entitlements,
    }


def _element_to_dict(element: ElementTree.Element) -> dict[str, Any]:
    if not list(element):
        return {element.tag: (element.text or "").strip()}

    output: dict[str, Any] = {}
    for child in element:
        value = _element_to_dict(child)
        child_value = value.get(child.tag, value)
        if child.tag in output:
            if not isinstance(output[child.tag], list):
                output[child.tag] = [output[child.tag]]
            output[child.tag].append(child_value)
        else:
            output[child.tag] = child_value
    return output


def _listify(value: Any) -> list[dict[str, Any]]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [v if isinstance(v, dict) else {"value": v} for v in value]
    if isinstance(value, dict):
        nested = value.get("item") or value.get("items") or value.get("asset") or value.get("window")
        if isinstance(nested, list):
            return [v if isinstance(v, dict) else {"value": v} for v in nested]
        return [value]
    return [{"value": value}]


def _string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

