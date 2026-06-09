# Mahiro Invest

Mahiro Invest is a personalized NSE stock screener, portfolio tracker, and earnings calendar. It lets each user create their own investor profiles, tune shopping-site style filters, run the screener across the NSE equity universe, save shortlists, and track portfolio/watchlist actions.

## Current Features

- JWT auth with local demo seed users.
- Persona engine with editable rules and presets: Conservative, Growth, Dividend, Momentum, and Banking-focused.
- Live debounced screener filters with sortable results.
- Full NSE equity universe seed from NSE's official EQ symbol list, with local fallback data when live data is unavailable.
- Saved screener screens such as "Today's shortlist" or "June quality picks".
- Stock detail with pass/fail reasons, rejected filters, raw metric values, charts, and data-quality labels.
- Watchlist and portfolio actions directly from screener rows.
- Portfolio P&L, sector allocation, alerts, earnings calendar, LLM explanation hooks, and ML anomaly service scaffolding.

## Local Setup

1. Copy env examples:

```powershell
Copy-Item .env.example .env
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

2. Start Postgres and Redis:

```powershell
docker compose up -d postgres redis
```

3. Start backend:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

4. Start frontend:

```powershell
cd frontend
npm install
npm run dev
```

5. Open `http://127.0.0.1:5173`.

Seed login:

- `investor@example.com`
- `mahiro123`

## Production Environment

Backend variables:

- `DATABASE_URL`: managed PostgreSQL URL from Railway, Render, Neon, or Supabase.
- `REDIS_URL`: managed Redis URL from Railway, Render, or Upstash.
- `JWT_SECRET`: long random secret. Never use the default in production.
- `CORS_ORIGINS`: deployed frontend origins, comma-separated.
- `ANTHROPIC_API_KEY`: optional, enables Claude explanations.

Frontend variables:

- `VITE_API_URL`: deployed FastAPI URL.

## Deployment Notes

Backend on Railway or Render:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add PostgreSQL and Redis services, then set `DATABASE_URL` and `REDIS_URL`.
- Set `CORS_ORIGINS` to the Vercel URL.

Frontend on Vercel:

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Set `VITE_API_URL` to the deployed backend URL.

## Data Quality

NSE/yfinance data can be incomplete. The UI labels data as:

- `Live`: freshly fetched.
- `Cached`: older fetched data.
- `Estimated`: generated fallback values used because live data was unavailable.
- `Missing`: important values are unavailable.

## Disclaimer

Mahiro Invest is an analysis tool, not financial advice. It does not guarantee returns or replace professional financial judgment.
