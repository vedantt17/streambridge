from __future__ import annotations

import re
import os
from collections import Counter
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import BACKEND_DIR, get_db
from app.services.ingestion import store_parsed_records
from app.services.parser import SUPPORTED_FEED_TYPES, parse_feed_file
from app.services.readiness import calculate_readiness
from app.services.validation import validate_feed

router = APIRouter(prefix="/api/feeds", tags=["feeds"])

UPLOAD_DIR = Path("/tmp/streambridge-uploads") if os.getenv("VERCEL") else BACKEND_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_BYTES = 8 * 1024 * 1024


@router.post("/upload", response_model=schemas.FeedUploadOut)
async def upload_feed(
    partner_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> models.FeedUpload:
    partner = db.get(models.Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found.")

    original_name = Path(file.filename or "partner-feed").name
    file_type = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if file_type not in SUPPORTED_FEED_TYPES:
        raise HTTPException(status_code=400, detail="Only JSON, XML, and CSV feeds are supported.")

    payload = await file.read()
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Feed upload exceeds 8 MB limit.")

    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", original_name)
    stored_name = f"{uuid4().hex}_{safe_name}"
    destination = (UPLOAD_DIR / stored_name).resolve()
    if UPLOAD_DIR.resolve() not in destination.parents:
        raise HTTPException(status_code=400, detail="Invalid upload path.")
    destination.write_bytes(payload)

    feed = models.FeedUpload(
        partner_id=partner_id,
        file_name=original_name,
        file_type=file_type,
        raw_file_path=str(destination),
        parse_status="Pending",
    )
    db.add(feed)
    db.commit()
    db.refresh(feed)
    return feed


@router.post("/{feed_id}/parse", response_model=schemas.ParseResult)
def parse_feed(feed_id: int, db: Session = Depends(get_db)) -> schemas.ParseResult:
    feed = db.get(models.FeedUpload, feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found.")

    parsed = parse_feed_file(feed.raw_file_path, feed.file_type)
    if parsed.errors:
        feed.parse_status = "Failed"
        feed.parser_error = "; ".join(parsed.errors)
        db.commit()
        return schemas.ParseResult(
            feed_id=feed.feed_id,
            parse_status=feed.parse_status,
            content_records=0,
            parser_error=feed.parser_error,
        )

    count = store_parsed_records(db, feed, parsed.records)
    return schemas.ParseResult(feed_id=feed.feed_id, parse_status="Parsed", content_records=count)


@router.post("/{feed_id}/validate", response_model=schemas.ValidationResult)
def validate_feed_endpoint(feed_id: int, db: Session = Depends(get_db)) -> schemas.ValidationResult:
    feed = db.get(models.FeedUpload, feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found.")
    try:
        errors = validate_feed(db, feed_id)
        readiness = calculate_readiness(db, feed.partner_id, feed_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    severity_counts = Counter(error.severity for error in errors)
    return schemas.ValidationResult(
        feed_id=feed_id,
        issue_count=len(errors),
        severity_counts=dict(severity_counts),
        readiness={
            "readiness_score": readiness.readiness_score,
            "critical_count": readiness.critical_count,
            "high_count": readiness.high_count,
            "valid_content_pct": readiness.valid_content_pct,
            "artwork_completion_pct": readiness.artwork_completion_pct,
            "entitlement_completion_pct": readiness.entitlement_completion_pct,
            "api_health_score": readiness.api_health_score,
        },
    )


@router.get("/{feed_id}/errors")
def get_feed_errors(feed_id: int, db: Session = Depends(get_db)) -> list[dict]:
    feed = db.get(models.FeedUpload, feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found.")
    errors = (
        db.query(models.ValidationError)
        .filter(models.ValidationError.feed_id == feed_id)
        .order_by(models.ValidationError.severity, models.ValidationError.created_at.desc())
        .all()
    )
    return [
        {
            "error_id": error.error_id,
            "content_id": error.content_id,
            "severity": error.severity,
            "category": error.category,
            "rule_name": error.rule_name,
            "error_message": error.error_message,
            "recommended_fix": error.recommended_fix,
            "status": error.status,
            "assigned_owner": error.assigned_owner,
            "created_at": error.created_at.isoformat(),
        }
        for error in errors
    ]
