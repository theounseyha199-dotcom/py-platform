from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PaymentMethod(str, Enum):
    CASH = "CASH"
    KHQR = "KHQR"
    CARD = "CARD"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentCreate(BaseModel):
    order_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_method: PaymentMethod


class PaymentRead(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
