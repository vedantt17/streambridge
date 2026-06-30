# API Documentation

OpenAPI docs are available at `/docs` when the backend is running.

## Partners

- `GET /api/partners`: list partner summaries with readiness, blockers, SLA age, region coverage, last feed, and entitlement status.
- `POST /api/partners`: create a partner.
- `GET /api/partners/{partner_id}`: get partner detail, feeds, issues, checks, and tasks.
- `GET /api/partners/{partner_id}/readiness`: latest readiness score.
- `GET /api/partners/{partner_id}/integration-checklist`: partner-ready checklist.
- `GET /api/partners/{partner_id}/troubleshooting-summary`: deterministic LLM-style summary.

## Feeds

- `POST /api/feeds/upload`: upload JSON/XML/CSV feed with `partner_id` and `file`.
- `POST /api/feeds/{feed_id}/parse`: parse feed into normalized records.
- `POST /api/feeds/{feed_id}/validate`: run validation rules and generate readiness score.
- `GET /api/feeds/{feed_id}/errors`: list validation errors for a feed.

## Operations

- `GET /api/issues/triage`: filter issues by severity, category, partner, and status.
- `PATCH /api/issues/{issue_id}`: update issue status, owner, or resolution notes.
- `POST /api/api-checks/run/{partner_id}`: simulate partner endpoint checks.
- `GET /api/api-checks/{partner_id}`: request/response history.
- `GET /api/dashboard/summary`: dashboard metrics and trend data.
- `GET /api/reports/product-feedback`: recurring issue and product-improvement report.

