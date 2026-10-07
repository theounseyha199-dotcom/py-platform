from contextlib import contextmanager
from decimal import Decimal
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.database import Base
from app.models.category import Category
from app.models.product import Product
from app.models.user import User


@contextmanager
def database_session() -> Iterator[Session]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as db:
            yield db
    finally:
        engine.dispose()


def user(db: Session, email: str = "customer@example.com", role: str = "CUSTOMER") -> User:
    result = User(name="Test User", email=email, password_hash="hash", role=role)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def product(db: Session, price: str = "2.50", available: bool = True) -> Product:
    category = Category(name="Coffee")
    db.add(category)
    db.flush()
    result = Product(name="Latte", price=Decimal(price), category_id=category.id, available=available)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def expect_error(callback, status_code: int) -> None:
    from app.core.exceptions import AppError

    try:
        callback()
    except AppError as exc:
        assert exc.status_code == status_code
    else:
        raise AssertionError(f"Expected {status_code} error")
