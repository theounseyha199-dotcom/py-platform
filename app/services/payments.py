from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.payment import Payment
from app.models.user import User
from app.repositories import payments as repo
from app.schemas.payment import PaymentCreate, PaymentMethod


def create_payment(db: Session, data: PaymentCreate, user: User) -> Payment:
    order = repo.get_order_for_payment(db, data.order_id)
    if order is None or (user.role == "CUSTOMER" and order.customer_id != user.id):
        raise AppError("Order not found", 404)
    if order.status == "CANCELLED":
        raise AppError("Cancelled order cannot be paid", 400)
    if data.amount != order.total_amount:
        raise AppError("Payment amount must match order total", 400)
    payments = repo.list_for_order(db, order.id)
    if any(payment.payment_status == "PAID" for payment in payments):
        raise AppError("Order is already paid", 409)
    if any(payment.payment_status == "PENDING" for payment in payments):
        raise AppError("Order already has a pending payment", 409)
    is_cash = data.payment_method == PaymentMethod.CASH
    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method=data.payment_method.value,
        payment_status="PAID" if is_cash else "PENDING",
        transaction_id=uuid4().hex.upper() if is_cash else None,
    )
    return repo.save(db, payment)


def get_payment(db: Session, payment_id: int, user: User) -> Payment:
    payment = repo.get(db, payment_id)
    if payment is None or (user.role == "CUSTOMER" and payment.order.customer_id != user.id):
        raise AppError("Payment not found", 404)
    return payment
