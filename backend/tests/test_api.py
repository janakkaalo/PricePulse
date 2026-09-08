"""API tests: auth, products CRUD, history, alerts, stats, scraper unit."""

import os

os.environ["DISABLE_SCHEDULER"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services import extract_price_from_html  # noqa: E402

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _register(email="test@example.com", password="password123"):
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code in (200, 201, 400), r.text


def _login(email="test@example.com", password="password123") -> str:
    _register(email, password)
    r = client.post("/api/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_health():
    r = client.get("/api/stats/health")
    assert r.status_code == 200


def test_auth_and_products_flow():
    token = _login()
    h = _headers(token)

    # create
    r = client.post(
        "/api/products",
        json={"name": "Test Widget", "url": "https://example.com/widget-1", "target_price": 50.0},
        headers=h,
    )
    assert r.status_code == 201, r.text
    pid = r.json()["id"]

    # list
    r = client.get("/api/products", headers=h)
    assert r.status_code == 200 and len(r.json()) >= 1

    # history (initial check creates >=1 point)
    r = client.get(f"/api/products/{pid}/history", headers=h)
    assert r.status_code == 200 and len(r.json()) >= 1

    # check-now
    r = client.post(f"/api/products/{pid}/check-now", headers=h)
    assert r.status_code == 200

    # dashboard
    r = client.get("/api/stats/dashboard", headers=h)
    assert r.status_code == 200
    assert r.json()["total_products"] >= 1

    # alerts list
    r = client.get("/api/alerts", headers=h)
    assert r.status_code == 200


def test_unauthorized():
    r = client.get("/api/products")
    assert r.status_code == 401


def test_scraper_extract():
    html = '<html><head><meta property="product:price:amount" content="42.50"/></head></html>'
    assert extract_price_from_html(html) == 42.50
    html2 = '<div class="price">$1,299.99</div>'
    assert extract_price_from_html(html2) == 1299.99
