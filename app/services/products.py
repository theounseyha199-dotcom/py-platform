from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.product import Product
from app.repositories import categories as category_repo
from app.repositories import products as repo
from app.schemas.product import ProductCreate, ProductUpdate


def _validate_category(db: Session, category_id: int) -> None:
    category = category_repo.get(db, category_id)
    if category is None or not category.active:
        raise AppError("Active category not found", 404)


def get_product(db: Session, product_id: int) -> Product:
    product = repo.get(db, product_id)
    if product is None:
        raise AppError("Product not found", 404)
    return product


def list_products(db: Session, category_id: int | None, available: bool | None, search: str | None) -> list[Product]:
    return repo.list_filtered(db, category_id, available, search)


def create_product(db: Session, data: ProductCreate) -> Product:
    _validate_category(db, data.category_id)
    return repo.save(db, Product(**data.model_dump()))


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = get_product(db, product_id)
    _validate_category(db, data.category_id)
    for field, value in data.model_dump().items():
        setattr(product, field, value)
    return repo.save(db, product)


def delete_product(db: Session, product_id: int) -> Product:
    product = get_product(db, product_id)
    product.available = False
    return repo.save(db, product)
