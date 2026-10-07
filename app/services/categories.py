from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.category import Category
from app.repositories import categories as repo
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Category:
    category = repo.get(db, category_id)
    if category is None or not category.active:
        raise AppError("Category not found", 404)
    return category


def list_categories(db: Session) -> list[Category]:
    return repo.list_active(db)


def _check_name(db: Session, name: str, current_id: int | None = None) -> None:
    existing = repo.get_by_name(db, name)
    if existing is not None and existing.id != current_id:
        raise AppError("Category name already exists", 409)


def create_category(db: Session, data: CategoryCreate) -> Category:
    _check_name(db, data.name)
    try:
        return repo.save(db, Category(**data.model_dump()))
    except IntegrityError:
        db.rollback()
        raise AppError("Category name already exists", 409) from None


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = get_category(db, category_id)
    _check_name(db, data.name, category.id)
    for field, value in data.model_dump().items():
        setattr(category, field, value)
    try:
        return repo.save(db, category)
    except IntegrityError:
        db.rollback()
        raise AppError("Category name already exists", 409) from None


def delete_category(db: Session, category_id: int) -> Category:
    category = get_category(db, category_id)
    category.active = False
    return repo.save(db, category)
