from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment


def get(db: Session, payment_id: int) -> Payment | None:
    return db.get(Payment, payment_id)


def get_order_for_payment(db: Session, order_id: int) -> Order | None:
    return db.scalar(select(Order).where(Order.id == order_id).with_for_update())


def list_for_order(db: Session, order_id: int) -> list[Payment]:
    return list(db.scalars(select(Payment).where(Payment.order_id == order_id)))


def save(db: Session, payment: Payment) -> Payment:
    try:
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    except Exception:
        db.rollback()
        raise
