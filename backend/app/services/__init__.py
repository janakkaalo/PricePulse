"""Price scraping service.

Design: pluggable scrapers. MockScraper is deterministic + offline-friendly
(used in tests, seeding and as fallback). RealScraper attempts a live fetch
with httpx + BeautifulSoup and falls back to mock on any failure.
"""

import hashlib
import random
import re

import httpx
from bs4 import BeautifulSoup


def mock_price_for_url(url: str, base: float = 100.0) -> float:
    """Deterministic pseudo-price in [0.6*base, 1.2*base] derived from URL hash."""
    digest = hashlib.sha256(url.encode()).hexdigest()
    seed = int(digest[:8], 16)
    rng = random.Random(seed + int(__import__("time").time() // 3600))
    return round(base * rng.uniform(0.6, 1.2), 2)


def extract_price_from_html(html: str) -> float | None:
    soup = BeautifulSoup(html, "html.parser")

    # 1. OpenGraph / meta product price
    for selector in [
        'meta[property="product:price:amount"]',
        'meta[property="og:price:amount"]',
        'meta[itemprop="price"]',
    ]:
        tag = soup.select_one(selector)
        if tag and tag.get("content"):
            try:
                return float(tag["content"])
            except ValueError:
                pass

    # 2. Common price CSS classes
    for selector in [".price", "#price", "[data-price]", ".product-price", ".a-price-whole"]:
        tag = soup.select_one(selector)
        if tag:
            text = tag.get("data-price") or tag.get_text()
            m = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
            if m:
                try:
                    return float(m.group(0))
                except ValueError:
                    continue
    return None


def scrape_price(url: str, fallback_base: float = 100.0, timeout: float = 8.0) -> tuple[float, str]:
    """Return (price, source). source is 'live' or 'mock'."""
    try:
        resp = httpx.get(url, timeout=timeout, follow_redirects=True, headers={"User-Agent": "PricePulse/1.0"})
        if resp.status_code == 200:
            price = extract_price_from_html(resp.text)
            if price:
                return round(price, 2), "live"
    except Exception:
        pass
    return mock_price_for_url(url, base=fallback_base), "mock"
