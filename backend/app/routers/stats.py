"""Dashboard stats endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
def dashboard(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    total = db.query(func.count(models.Product.id)).filter(models.Product.user_id == user.id).scalar() or 0
    active = (
        db.query(func.count(models.Product.id))
        .filter(models.Product.user_id == user.id, models.Product.is_active == True)  # noqa: E712
        .scalar()
        or 0
    )
    unread = (
        db.query(func.count(models.Alert.id))
        .join(models.Product, models.Alert.product_id == models.Product.id)
        .filter(models.Product.user_id == user.id, models.Alert.is_read == False)  # noqa: E712
        .scalar()
        or 0
    )
    avg_price = (
        db.query(func.avg(models.Product.current_price)).filter(models.Product.user_id == user.id).scalar()
    )
    best = (
        db.query(models.Product)
        .filter(models.Product.user_id == user.id, models.Product.current_price.is_not(None))
        .order_by((models.Product.current_price - models.Product.target_price).asc())
        .first()
    )
    return schemas.DashboardStats(
        total_products=total,
        active_products=active,
        active_alerts=unread,
        avg_current_price=round(float(avg_price), 2) if avg_price else None,
        best_deal_product_id=best.id if best else None,
    )


@router.get("/health")
def health():
    return {"status": "ok"}
