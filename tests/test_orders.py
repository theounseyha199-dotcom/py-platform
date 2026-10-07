from decimal import Decimal

from app.schemas.order import OrderCreate, OrderItemCreate, OrderStatus
from app.services import orders
from tests.helpers import expect_error, product, database_session, user


def test_order_total_snapshot_ownership_and_transitions() -> None:
    with database_session() as db:
        customer = user(db)
        other = user(db, "other@example.com")
        item = product(db)
        order = orders.create_order(db, customer, OrderCreate(items=[OrderItemCreate(product_id=item.id, quantity=2)]))
        assert order.total_amount == Decimal("5.00")
        assert order.items[0].subtotal == Decimal("5.00")
        item.price = Decimal("9.00")
        db.commit()
        assert orders.get_order(db, order.id, customer).items[0].unit_price == Decimal("2.50")
        assert orders.list_orders(db, other) == []
        expect_error(lambda: orders.get_order(db, order.id, other), 404)
        for state in (OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.COMPLETED):
            orders.update_status(db, order.id, state)
        expect_error(lambda: orders.update_status(db, order.id, OrderStatus.CANCELLED), 400)


def test_invalid_order_and_cancellation() -> None:
    with database_session() as db:
        customer = user(db)
        item = product(db, available=False)
        expect_error(lambda: orders.create_order(db, customer, OrderCreate(items=[OrderItemCreate(product_id=item.id, quantity=1)])), 400)
        item.available = True
        db.commit()
        order = orders.create_order(db, customer, OrderCreate(items=[OrderItemCreate(product_id=item.id, quantity=1)]))
        assert orders.update_status(db, order.id, OrderStatus.CANCELLED).status == "CANCELLED"
        expect_error(lambda: orders.update_status(db, order.id, OrderStatus.CONFIRMED), 400)
