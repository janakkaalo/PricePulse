"""Central configuration loaded from environment variables."""

import os


def get_setting(name: str, default: str) -> str:
    return os.getenv(name, default)


SECRET_KEY = get_setting("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_setting("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
DATABASE_URL = get_setting("DATABASE_URL", "sqlite:///./pricepulse.db")
SCRAPE_INTERVAL_MINUTES = int(get_setting("SCRAPE_INTERVAL_MINUTES", "15"))
DISABLE_SCHEDULER = get_setting("DISABLE_SCHEDULER", "0") == "1"
