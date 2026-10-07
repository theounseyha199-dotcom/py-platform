from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import success
from app.core.security import require_staff
from app.schemas.inventory import IngredientCreate, IngredientRead, IngredientUpdate, RecipeItem, RecipeRead
from app.services import inventory as service


router = APIRouter(prefix="/inventory", tags=["inventory"], dependencies=[Depends(require_staff)])


@router.post("/ingredients", status_code=status.HTTP_201_CREATED)
def create_ingredient(data: IngredientCreate, db: Session = Depends(get_db)) -> dict[str, object]:
    ingredient = service.create_ingredient(db, data)
    return success("Ingredient created successfully", IngredientRead.model_validate(ingredient).model_dump(mode="json"))


@router.get("/ingredients")
def list_ingredients(db: Session = Depends(get_db)) -> dict[str, object]:
    data = [IngredientRead.model_validate(item).model_dump(mode="json") for item in service.list_ingredients(db)]
    return success("Ingredients retrieved successfully", data)


@router.get("/ingredients/{ingredient_id}")
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    ingredient = service.get_ingredient(db, ingredient_id)
    return success("Ingredient retrieved successfully", IngredientRead.model_validate(ingredient).model_dump(mode="json"))


@router.put("/ingredients/{ingredient_id}")
def update_ingredient(ingredient_id: int, data: IngredientUpdate, db: Session = Depends(get_db)) -> dict[str, object]:
    ingredient = service.update_ingredient(db, ingredient_id, data)
    return success("Ingredient updated successfully", IngredientRead.model_validate(ingredient).model_dump(mode="json"))


@router.get("/products/{product_id}/ingredients")
def get_recipe(product_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    data = [RecipeRead.model_validate(item).model_dump(mode="json") for item in service.get_recipe(db, product_id)]
    return success("Recipe retrieved successfully", data)


@router.put("/products/{product_id}/ingredients")
def replace_recipe(product_id: int, items: list[RecipeItem], db: Session = Depends(get_db)) -> dict[str, object]:
    data = [RecipeRead.model_validate(item).model_dump(mode="json") for item in service.replace_recipe(db, product_id, items)]
    return success("Recipe updated successfully", data)
