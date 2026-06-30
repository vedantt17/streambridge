from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, init_db
from app.routers import api_checks, dashboard, feeds, issues, partners, reports
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_if_empty(db)
    yield


app = FastAPI(
    title="StreamBridge Partner Onboarding API",
    description="Validation, readiness, troubleshooting, and reporting APIs for TV partner integrations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(partners.router)
app.include_router(feeds.router)
app.include_router(issues.router)
app.include_router(api_checks.router)
app.include_router(dashboard.router)
app.include_router(reports.router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

