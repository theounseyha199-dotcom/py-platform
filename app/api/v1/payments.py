from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import success
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentRead
from app.services import payments as service


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create(data: PaymentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    payment = service.create_payment(db, data, user)
    return success("Payment created successfully", PaymentRead.model_validate(payment).model_dump(mode="json"))


@router.get("/{payment_id}")
def get_one(payment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    payment = service.get_payment(db, payment_id, user)
    return success("Payment retrieved successfully", PaymentRead.model_validate(payment).model_dump(mode="json"))
