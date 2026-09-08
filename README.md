# ⚡ PricePulse — Track prices, catch deals

Full-stack price tracker: save any product URL, auto-check prices on a schedule, visualize history, and get alerts when prices drop below your target.

**Stack:** Python FastAPI + SQLAlchemy + SQLite/Postgres · React + TypeScript + Vite + Recharts · JWT auth · APScheduler scraper · Docker · GitHub Actions

## Features
- 🔐 JWT register/login (OAuth2 password flow)
- 📦 Product CRUD (name, URL, target price) — scoped per user
- 🔄 Price engine: pluggable scraper (`httpx` + `BeautifulSoup`, live + deterministic mock fallback)
- ⏰ Background re-checks every 15 min (APScheduler) + manual “Check now”
- 📈 Price history API + Recharts graph (`/products/:id`)
- 🔔 Deal alerts auto-created when `current <= target`, mark-as-read UI
- 📊 Dashboard stats: totals, active, unread alerts, avg price, best deal

## Motivation

I waste time re-checking prices and miss drops. PricePulse solves it by tracking any product URL, recording history automatically, and alerting when `current <= target` — with auth, graphs, and a demoable dashboard for my portfolio.

## Quick Start

### 1. Backend
```bash
python3 -m virtualenv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

# seed demo data (demo@example.com / demo1234) — run from backend/ dir:
cd backend
DISABLE_SCHEDULER=1 DATABASE_URL="sqlite:///./pricepulse.db" python -m app.seed
DISABLE_SCHEDULER=0 uvicorn app.main:app --reload --port 8000
# docs: http://127.0.0.1:8000/docs
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev     # http://localhost:5173 (proxies /api -> :8000)
```

### 3. Docker (optional)
```bash
docker compose up --build
# api :8000, web :5173
```

## Usage

Full API reference (all `/api/*` except register/login/health need `Authorization: Bearer <token>`):

```
POST /api/auth/register {email, password} -> User
POST /api/auth/login (form: username, password) -> {access_token}
GET/POST /api/products
GET/PUT/DELETE /api/products/{id}
GET /api/products/{id}/history?days=30
POST /api/products/{id}/check-now
GET /api/alerts, PUT /api/alerts/{id}/read
GET /api/stats/dashboard, GET /api/stats/health
```

### Examples

Track a product:

```bash
curl -X POST http://127.0.0.1:8000/api/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Sony XM5","url":"https://example.com/sony-xm5","target_price":249.99}'
```

History + manual re-check:

```bash
curl "http://127.0.0.1:8000/api/products/1/history?days=90" -H "Authorization: Bearer $TOKEN"
curl -X POST http://127.0.0.1:8000/api/products/1/check-now -H "Authorization: Bearer $TOKEN"
```

Env knobs (`backend/.env.example`):

```
SECRET_KEY=dev-secret-change-me
DATABASE_URL=sqlite:///./pricepulse.db
SCRAPE_INTERVAL_MINUTES=15
```

## Contributing

## Contributing

### Clone the repo

```bash
git clone https://github.com/janakkaalo/PricePulse.git
cd PricePulse
```

### Backend setup

```bash
python3 -m virtualenv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
DISABLE_SCHEDULER=1 DATABASE_URL="sqlite:///./pricepulse.db" python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

### Run the test suite

```bash
DISABLE_SCHEDULER=1 DATABASE_URL="sqlite:///./test.db" pytest backend/tests -v
cd frontend && npm run build
```

### Submit a pull request

Fork the repo and open a PR to `main`. Keep commits scoped (`feat:`, `fix:`, `chore:`) with tests for backend changes.

## Project structure
```
backend/app/{main,config,database,models,schemas,auth}.py
backend/app/routers/{auth,products,alerts,stats}.py
backend/app/services/{scraper,tracker}.py
backend/tests/test_api.py
frontend/src/{api,auth,pages,components}
```

## How the scraper works
`scrape_price(url)` tries live fetch → parses `product:price:amount`, `og:price:amount`, `.price` etc. → falls back to deterministic mock price (hash of URL + hour) so demo/tests work offline. `tracker.check_product()` stores a `PricePoint`, updates `current_price`, creates one unread `Alert` per price-drop crossing.

## Roadmap
- Email/webhook alerts, real store adapters (Amazon etc.)
- Postgres + Alembic migrations, refresh tokens
- Frontend vitest + pagination/filters

Built as Boot.dev capstone — 40h+ scope, clean commits, tested.
