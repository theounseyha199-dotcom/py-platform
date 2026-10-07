from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import success
from app.core.security import get_current_user, require_staff
from app.models.user import User
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate
from app.services import orders as service


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create(data: OrderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    order = service.create_order(db, user, data)
    return success("Order created successfully", OrderRead.model_validate(order).model_dump(mode="json"))


@router.get("")
def list_all(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    data = [OrderRead.model_validate(order).model_dump(mode="json") for order in service.list_orders(db, user)]
    return success("Orders retrieved successfully", data)


@router.get("/{order_id}")
def get_one(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, object]:
    order = service.get_order(db, order_id, user)
    return success("Order retrieved successfully", OrderRead.model_validate(order).model_dump(mode="json"))


@router.patch("/{order_id}/status", dependencies=[Depends(require_staff)])
def update_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db)) -> dict[str, object]:
    order = service.update_status(db, order_id, data.status)
    return success("Order status updated successfully", OrderRead.model_validate(order).model_dump(mode="json"))
