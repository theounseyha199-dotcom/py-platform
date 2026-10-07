from decimal import Decimal

from app.schemas.order import OrderCreate, OrderItemCreate
from app.schemas.payment import PaymentCreate, PaymentMethod
from app.services import orders, payments
from tests.helpers import expect_error, product, database_session, user


def test_cash_payment_amount_and_duplicate() -> None:
    with database_session() as db:
        customer = user(db)
        other = user(db, "other@example.com")
        item = product(db)
        order = orders.create_order(db, customer, OrderCreate(items=[OrderItemCreate(product_id=item.id, quantity=2)]))
        expect_error(lambda: payments.create_payment(db, PaymentCreate(order_id=order.id, amount=Decimal("1.00"), payment_method=PaymentMethod.CASH), customer), 400)
        payment = payments.create_payment(db, PaymentCreate(order_id=order.id, amount=Decimal("5.00"), payment_method=PaymentMethod.CASH), customer)
        assert payment.payment_status == "PAID"
        assert payments.get_payment(db, payment.id, customer).id == payment.id
        expect_error(lambda: payments.get_payment(db, payment.id, other), 404)
        expect_error(lambda: payments.create_payment(db, PaymentCreate(order_id=order.id, amount=Decimal("5.00"), payment_method=PaymentMethod.CASH), customer), 409)
