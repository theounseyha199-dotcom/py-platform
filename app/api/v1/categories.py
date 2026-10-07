from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import success
from app.core.security import require_admin
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import categories as service


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create(data: CategoryCreate, db: Session = Depends(get_db)) -> dict[str, object]:
    category = service.create_category(db, data)
    return success("Category created successfully", CategoryRead.model_validate(category).model_dump(mode="json"))


@router.get("")
def list_all(db: Session = Depends(get_db)) -> dict[str, object]:
    data = [CategoryRead.model_validate(item).model_dump(mode="json") for item in service.list_categories(db)]
    return success("Categories retrieved successfully", data)


@router.get("/{category_id}")
def get_one(category_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    category = service.get_category(db, category_id)
    return success("Category retrieved successfully", CategoryRead.model_validate(category).model_dump(mode="json"))


@router.put("/{category_id}", dependencies=[Depends(require_admin)])
def update(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)) -> dict[str, object]:
    category = service.update_category(db, category_id, data)
    return success("Category updated successfully", CategoryRead.model_validate(category).model_dump(mode="json"))


@router.delete("/{category_id}", dependencies=[Depends(require_admin)])
def delete(category_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    service.delete_category(db, category_id)
    return success("Category deleted successfully", None)
