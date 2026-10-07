from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product


def get(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id, options=[selectinload(Product.image)])


def list_filtered(
    db: Session,
    category_id: int | None = None,
    available: bool | None = None,
    search: str | None = None,
) -> list[Product]:
    query = select(Product).options(selectinload(Product.image)).order_by(Product.id)
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
    if available is not None:
        query = query.where(Product.available.is_(available))
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    return list(db.scalars(query))


def save(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
