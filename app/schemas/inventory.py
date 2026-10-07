from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    quantity: Decimal = Field(ge=0, max_digits=12, decimal_places=3)
    unit: str = Field(min_length=1, max_length=30)
    minimum_stock: Decimal = Field(ge=0, max_digits=12, decimal_places=3)

    @field_validator("name", "unit")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty")
        return value


class IngredientUpdate(IngredientCreate):
    active: bool = True


class IngredientRead(IngredientUpdate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecipeItem(BaseModel):
    ingredient_id: int = Field(gt=0)
    quantity_required: Decimal = Field(gt=0, max_digits=12, decimal_places=3)


class RecipeRead(RecipeItem):
    product_id: int

    model_config = ConfigDict(from_attributes=True)
