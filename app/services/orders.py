from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.user import User
from app.repositories import orders as repo
from app.repositories import products as product_repo
from app.schemas.order import OrderCreate, OrderStatus


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "PENDING": {"CONFIRMED", "CANCELLED"},
    "CONFIRMED": {"PREPARING", "CANCELLED"},
    "PREPARING": {"READY"},
    "READY": {"COMPLETED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}


def create_order(db: Session, customer: User, data: OrderCreate) -> Order:
    if customer.role != "CUSTOMER":
        raise AppError("Customer access required", 403)
    product_ids = [item.product_id for item in data.items]
    if len(product_ids) != len(set(product_ids)):
        raise AppError("Duplicate products in order", 422)
    items: list[OrderItem] = []
    total = Decimal("0.00")
    for requested in data.items:
        product = product_repo.get(db, requested.product_id)
        if product is None or not product.available:
            raise AppError(f"Product {requested.product_id} is unavailable", 400)
        subtotal = product.price * requested.quantity
        items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            unit_price=product.price,
            quantity=requested.quantity,
            subtotal=subtotal,
        ))
        total += subtotal
    order = Order(
        order_number=uuid4().hex.upper(),
        customer_id=customer.id,
        status="PENDING",
        total_amount=total,
        items=items,
    )
    return repo.save_order(db, order)


def list_orders(db: Session, user: User) -> list[Order]:
    return repo.list_orders(db, user.id if user.role == "CUSTOMER" else None)


def get_order(db: Session, order_id: int, user: User) -> Order:
    order = repo.get_order(db, order_id)
    if order is None or (user.role == "CUSTOMER" and order.customer_id != user.id):
        raise AppError("Order not found", 404)
    return order


def update_status(db: Session, order_id: int, status: OrderStatus) -> Order:
    order = repo.get_order(db, order_id)
    if order is None:
        raise AppError("Order not found", 404)
    if status.value not in ALLOWED_TRANSITIONS[order.status]:
        raise AppError("Invalid order status transition", 400)
    order.status = status.value
    return repo.save_order(db, order)
