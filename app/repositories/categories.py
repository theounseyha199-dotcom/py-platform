from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category


def get(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_by_name(db: Session, name: str) -> Category | None:
    return db.scalar(select(Category).where(func.lower(Category.name) == name.lower()))


def list_active(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).where(Category.active.is_(True)).order_by(Category.id)))


def save(db: Session, category: Category) -> Category:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
