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

## Quickstart (local)

### 1. Backend
```bash
python3 -m virtualenv .venv && source .venv/bin/activate  # or: virtualenv /tmp/ppvenv
pip install -r backend/requirements.txt

# seed demo data (demo@example.com / demo1234)
DISABLE_SCHEDULER=1 DATABASE_URL="sqlite:///./pricepulse.db" python -m app.seed
# run from backend/ dir:
cd backend
DISABLE_SCHEDULER=0 uvicorn app.main:app --reload --port 8000
# docs: http://127.0.0.1:8000/docs
```

### 2. Frontend
```bash
cd frontend
npm install
npm run build   # verify
npm run dev     # http://localhost:5173 (proxies /api -> :8000)
```

### 3. Docker (optional)
```bash
docker compose up --build
# api :8000, web :5173
```

## Tests
```bash
DISABLE_SCHEDULER=1 DATABASE_URL="sqlite:///./test.db" pytest backend/tests -v
cd frontend && npm run build  # typecheck + prod build
```

## API (v1)
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
