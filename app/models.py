from pydantic import BaseModel, Field, validator
from typing import List
from uuid import uuid4
from datetime import datetime
from .utils import generate_order_id


class OrderRequest(BaseModel):
    """Model for incoming order requests."""

    items: List[str] = Field(..., min_items=1)
    payment_amount: float = Field(..., gt=0)

    @validator("items")
    def items_must_not_be_empty(cls, val):
        if not val:
            raise ValueError("items list cannot be empty")
        return val

    @validator("payment_amount")
    def payment_amount_must_be_positive(cls, val):
        if val <= 0:
            raise ValueError("payment amount must be positive")
        return val


class OrderResponse(BaseModel):
    """Model for order responses."""

    order_id: str
    status: str


class Order(BaseModel):
    """Full order model for database storage."""

    order_id: str = Field(default_factory=generate_order_id)
    items: List[str]
    payment_amount: float
    status: str = "processed"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
