"""Alert listing + mark-as-read."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[schemas.AlertOut])
def list_alerts(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rows = (
        db.query(models.Alert, models.Product.name)
        .join(models.Product, models.Alert.product_id == models.Product.id)
        .filter(models.Product.user_id == user.id)
        .order_by(models.Alert.created_at.desc())
        .all()
    )
    out: list[schemas.AlertOut] = []
    for alert, pname in rows:
        item = schemas.AlertOut.model_validate(alert)
        item.product_name = pname
        out.append(item)
    return out


@router.put("/{alert_id}/read", response_model=schemas.AlertOut)
def mark_read(alert_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    alert = (
        db.query(models.Alert)
        .join(models.Product, models.Alert.product_id == models.Product.id)
        .filter(models.Alert.id == alert_id, models.Product.user_id == user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    item = schemas.AlertOut.model_validate(alert)
    item.product_name = alert.product.name
    return item
