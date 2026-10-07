from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order


def get_order(db: Session, order_id: int) -> Order | None:
    return db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))


def list_orders(db: Session, customer_id: int | None = None) -> list[Order]:
    query = select(Order).options(selectinload(Order.items)).order_by(Order.id.desc())
    if customer_id is not None:
        query = query.where(Order.customer_id == customer_id)
    return list(db.scalars(query))


def save_order(db: Session, order: Order) -> Order:
    try:
        db.add(order)
        db.commit()
        db.refresh(order)
        return get_order(db, order.id) or order
    except Exception:
        db.rollback()
        raise
