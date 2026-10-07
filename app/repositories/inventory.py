from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient
from app.models.product_ingredient import ProductIngredient


def get_ingredient(db: Session, ingredient_id: int) -> Ingredient | None:
    return db.get(Ingredient, ingredient_id)


def get_by_name(db: Session, name: str) -> Ingredient | None:
    return db.scalar(select(Ingredient).where(func.lower(Ingredient.name) == name.lower()))


def list_ingredients(db: Session) -> list[Ingredient]:
    return list(db.scalars(select(Ingredient).order_by(Ingredient.id)))


def save_ingredient(db: Session, ingredient: Ingredient) -> Ingredient:
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


def get_recipe(db: Session, product_id: int) -> list[ProductIngredient]:
    return list(db.scalars(select(ProductIngredient).where(ProductIngredient.product_id == product_id)))


def replace_recipe(db: Session, product_id: int, items: list[ProductIngredient]) -> list[ProductIngredient]:
    try:
        for old in get_recipe(db, product_id):
            db.delete(old)
        db.flush()
        db.add_all(items)
        db.commit()
        return get_recipe(db, product_id)
    except Exception:
        db.rollback()
        raise
