"""Shared price-check logic used by API routes and background scheduler."""

from datetime import datetime

from sqlalchemy.orm import Session

from .. import models
from . import scrape_price


def check_product(db: Session, product: models.Product) -> models.PricePoint:
    base = product.current_price or product.target_price * 1.2
    price, _source = scrape_price(product.url, fallback_base=base)
    product.current_price = price
    point = models.PricePoint(product_id=product.id, price=price, checked_at=datetime.utcnow())
    db.add(point)

    # Generate alert once per crossing: only if no unread alert for this product.
    if price <= product.target_price:
        existing = (
            db.query(models.Alert)
            .filter(models.Alert.product_id == product.id, models.Alert.is_read == False)  # noqa: E712
            .first()
        )
        if not existing:
            db.add(
                models.Alert(
                    product_id=product.id,
                    trigger_price=price,
                    message=f"{product.name} dropped to ${price:.2f} (target ${product.target_price:.2f})",
                )
            )
    db.commit()
    db.refresh(point)
    return point


def check_all_active(db: Session, limit: int = 100) -> int:
    products = db.query(models.Product).filter(models.Product.is_active == True).limit(limit).all()  # noqa: E712
    for p in products:
        try:
            check_product(db, p)
        except Exception:
            db.rollback()
            continue
    return len(products)
