"""Product CRUD + price history + manual re-check."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..services.tracker import check_product

router = APIRouter(prefix="/api/products", tags=["products"])


def _get_owned(db: Session, user_id: int, product_id: int) -> models.Product:
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id, models.Product.user_id == user_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def _to_out(p: models.Product) -> schemas.ProductOut:
    return schemas.ProductOut(
        id=p.id,
        name=p.name,
        url=p.url,
        target_price=p.target_price,
        current_price=p.current_price,
        image_url=p.image_url,
        is_active=p.is_active,
        created_at=p.created_at,
        deal=bool(p.current_price is not None and p.current_price <= p.target_price),
    )


@router.get("", response_model=list[schemas.ProductOut])
def list_products(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    products = db.query(models.Product).filter(models.Product.user_id == user.id).order_by(models.Product.created_at.desc()).all()
    return [_to_out(p) for p in products]


@router.post("", response_model=schemas.ProductOut, status_code=201)
def create_product(
    payload: schemas.ProductCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    dup = db.query(models.Product).filter(models.Product.user_id == user.id, models.Product.url == payload.url).first()
    if dup:
        raise HTTPException(status_code=400, detail="You already track this URL")
    product = models.Product(
        user_id=user.id,
        name=payload.name,
        url=str(payload.url),
        target_price=payload.target_price,
        image_url=payload.image_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    # Initial price check so UI has data immediately.
    try:
        check_product(db, product)
        db.refresh(product)
    except Exception:
        pass
    return _to_out(product)


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return _to_out(_get_owned(db, user.id, product_id))


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int, payload: schemas.ProductUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    p = _get_owned(db, user.id, product_id)
    if payload.name is not None:
        p.name = payload.name
    if payload.target_price is not None:
        p.target_price = payload.target_price
    if payload.is_active is not None:
        p.is_active = payload.is_active
    if payload.image_url is not None:
        p.image_url = payload.image_url
    db.commit()
    db.refresh(p)
    return _to_out(p)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    p = _get_owned(db, user.id, product_id)
    db.delete(p)
    db.commit()
    return None


@router.get("/{product_id}/history", response_model=list[schemas.PricePointOut])
def history(product_id: int, days: int = 30, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    p = _get_owned(db, user.id, product_id)
    since = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(models.PricePoint)
        .filter(models.PricePoint.product_id == p.id, models.PricePoint.checked_at >= since)
        .order_by(models.PricePoint.checked_at.asc())
        .all()
    )


@router.post("/{product_id}/check-now", response_model=schemas.PricePointOut)
def check_now(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    p = _get_owned(db, user.id, product_id)
    return check_product(db, p)
