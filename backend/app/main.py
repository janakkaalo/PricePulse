"""FastAPI entrypoint with CORS, routers and background scheduler."""

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config, models
from .database import Base, SessionLocal, engine
from .routers import alerts, auth, products, stats
from .services.tracker import check_all_active

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PricePulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(alerts.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {"name": "PricePulse API", "docs": "/docs", "health": "/api/stats/health"}


def _scheduled_job():
    db = SessionLocal()
    try:
        check_all_active(db)
    finally:
        db.close()


scheduler: BackgroundScheduler | None = None
if not config.DISABLE_SCHEDULER:
    scheduler = BackgroundScheduler()
    scheduler.add_job(_scheduled_job, "interval", minutes=config.SCRAPE_INTERVAL_MINUTES)
    scheduler.start()
