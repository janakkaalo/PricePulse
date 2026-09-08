"""Pydantic request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginForm(BaseModel):
    email: EmailStr
    password: str


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=8, max_length=2000)
    target_price: float = Field(gt=0)
    image_url: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    target_price: float | None = Field(default=None, gt=0)
    is_active: bool | None = None
    image_url: str | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    url: str
    target_price: float
    current_price: float | None
    image_url: str | None
    is_active: bool
    created_at: datetime
    deal: bool = False

    class Config:
        from_attributes = True


class PricePointOut(BaseModel):
    id: int
    price: float
    checked_at: datetime

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: int
    product_id: int
    product_name: str = ""
    trigger_price: float
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_products: int
    active_products: int
    active_alerts: int
    avg_current_price: float | None
    best_deal_product_id: int | None
