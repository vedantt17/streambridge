# Deployment

## Local Development

Run the backend on port `8000` and the frontend on port `5173`.

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

## Docker Compose

```bash
docker compose up --build
```

Services:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

## Production Hardening

- Use PostgreSQL instead of SQLite.
- Store uploads in managed object storage.
- Add authentication, authorization, audit logging, and rate limiting.
- Run ingestion and API replay checks as background jobs.
- Restrict CORS to trusted origins.
- Add structured logging and error monitoring.

