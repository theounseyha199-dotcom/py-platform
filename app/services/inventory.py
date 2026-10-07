from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.ingredient import Ingredient
from app.models.product_ingredient import ProductIngredient
from app.repositories import inventory as repo
from app.repositories import products as product_repo
from app.schemas.inventory import IngredientCreate, IngredientUpdate, RecipeItem


def list_ingredients(db: Session) -> list[Ingredient]:
    return repo.list_ingredients(db)


def get_ingredient(db: Session, ingredient_id: int) -> Ingredient:
    ingredient = repo.get_ingredient(db, ingredient_id)
    if ingredient is None:
        raise AppError("Ingredient not found", 404)
    return ingredient


def create_ingredient(db: Session, data: IngredientCreate) -> Ingredient:
    if repo.get_by_name(db, data.name):
        raise AppError("Ingredient name already exists", 409)
    try:
        return repo.save_ingredient(db, Ingredient(**data.model_dump()))
    except IntegrityError:
        db.rollback()
        raise AppError("Ingredient name already exists", 409) from None


def update_ingredient(db: Session, ingredient_id: int, data: IngredientUpdate) -> Ingredient:
    ingredient = get_ingredient(db, ingredient_id)
    duplicate = repo.get_by_name(db, data.name)
    if duplicate and duplicate.id != ingredient.id:
        raise AppError("Ingredient name already exists", 409)
    for field, value in data.model_dump().items():
        setattr(ingredient, field, value)
    try:
        return repo.save_ingredient(db, ingredient)
    except IntegrityError:
        db.rollback()
        raise AppError("Ingredient name already exists", 409) from None


def get_recipe(db: Session, product_id: int) -> list[ProductIngredient]:
    if product_repo.get(db, product_id) is None:
        raise AppError("Product not found", 404)
    return repo.get_recipe(db, product_id)


def replace_recipe(db: Session, product_id: int, items: list[RecipeItem]) -> list[ProductIngredient]:
    if product_repo.get(db, product_id) is None:
        raise AppError("Product not found", 404)
    ids = [item.ingredient_id for item in items]
    if len(ids) != len(set(ids)):
        raise AppError("Duplicate ingredients in recipe", 422)
    for ingredient_id in ids:
        ingredient = repo.get_ingredient(db, ingredient_id)
        if ingredient is None or not ingredient.active:
            raise AppError(f"Active ingredient {ingredient_id} not found", 404)
    rows = [ProductIngredient(product_id=product_id, **item.model_dump()) for item in items]
    return repo.replace_recipe(db, product_id, rows)
