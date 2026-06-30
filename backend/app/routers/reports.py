from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.reports import product_feedback_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/product-feedback")
def get_product_feedback_report(db: Session = Depends(get_db)) -> dict:
    return product_feedback_report(db)

