from __future__ import annotations

import random
from datetime import datetime

from sqlalchemy.orm import Session

from app import models


ENDPOINTS = [
    "/metadata/v1/feed",
    "/availability/v1/windows",
    "/playback/v1/manifest",
    "/entitlements/v1/packages",
    "/captions/v1/status",
]

ERRORS = {
    401: "Authentication token rejected by partner API.",
    404: "Endpoint path not found in partner configuration.",
    409: "Package ID conflicts with existing launch configuration.",
    429: "Partner API throttled validation requests.",
    500: "Partner API returned an internal server error.",
    504: "Partner API timed out before returning a response.",
}


def run_partner_api_checks(db: Session, partner_id: int) -> list[models.ApiCheck]:
    partner = db.get(models.Partner, partner_id)
    if not partner:
        raise ValueError(f"Partner {partner_id} was not found.")

    seed = f"{partner.partner_name}-{datetime.utcnow().date()}-{db.query(models.ApiCheck).count()}"
    rng = random.Random(seed)
    checks: list[models.ApiCheck] = []
    for endpoint in ENDPOINTS:
        status_roll = rng.random()
        if status_roll < 0.72:
            status = 200
        elif status_roll < 0.84:
            status = rng.choice([429, 504])
        else:
            status = rng.choice([401, 404, 409, 500])

        latency = rng.randint(90, 1800 if status == 200 else 5200)
        timed_out = latency > 3500 or status == 504
        check_status = "Healthy" if status == 200 and not timed_out else "Failed"
        check = models.ApiCheck(
            partner_id=partner_id,
            endpoint=endpoint,
            http_status=504 if timed_out else status,
            latency_ms=latency,
            check_status=check_status,
            checked_at=datetime.utcnow(),
            error_message=None if check_status == "Healthy" else ERRORS.get(504 if timed_out else status),
        )
        db.add(check)
        checks.append(check)

    db.commit()
    for check in checks:
        db.refresh(check)
    return checks

