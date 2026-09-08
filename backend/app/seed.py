"""Seed demo data: demo@example.com / demo1234 + 3 products with history."""

from datetime import datetime, timedelta
import random

from .auth import hash_password
from .database import Base, SessionLocal, engine
from . import models

Base.metadata.create_all(bind=engine)

db = SessionLocal()
email = "demo@example.com"
user = db.query(models.User).filter(models.User.email == email).first()
if not user:
    user = models.User(email=email, password_hash=hash_password("demo1234"))
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"created user {email}")

samples = [
    ("Sony WH-1000XM5 Headphones", "https://example.com/sony-xm5", 249.99, 329.00),
    ("LEGO Star Wars Set", "https://example.com/lego-sw", 59.99, 79.99),
    ("Espresso Machine", "https://example.com/espresso", 399.00, 449.00),
]
random.seed(7)
for name, url, target, current in samples:
    exists = db.query(models.Product).filter(models.Product.user_id == user.id, models.Product.url == url).first()
    if exists:
        continue
    p = models.Product(user_id=user.id, name=name, url=url, target_price=target, current_price=current)
    db.add(p)
    db.commit()
    db.refresh(p)
    # 14 days of history trending down
    for i in range(14, 0, -1):
        price = round(current * (1 + random.uniform(-0.03, 0.08) * (i / 14)), 2)
        db.add(models.PricePoint(product_id=p.id, price=price, checked_at=datetime.utcnow() - timedelta(days=i)))
    db.add(models.PricePoint(product_id=p.id, price=current, checked_at=datetime.utcnow()))
    db.commit()
    print(f"seeded {name}")
db.close()
print("done. login with demo@example.com / demo1234")
