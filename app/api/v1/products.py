from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import success
from app.core.security import require_admin
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services import products as service


router = APIRouter(prefix="/products", tags=["products"])


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create(data: ProductCreate, db: Session = Depends(get_db)) -> dict[str, object]:
    product = service.create_product(db, data)
    return success("Product created successfully", ProductRead.model_validate(product).model_dump(mode="json"))


@router.get("")
def list_all(
    category_id: int | None = None,
    available: bool | None = None,
    search: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    products = service.list_products(db, category_id, available, search)
    data = [ProductRead.model_validate(item).model_dump(mode="json") for item in products]
    return success("Products retrieved successfully", data)


@router.get("/{product_id}")
def get_one(product_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    product = service.get_product(db, product_id)
    return success("Product retrieved successfully", ProductRead.model_validate(product).model_dump(mode="json"))


@router.put("/{product_id}", dependencies=[Depends(require_admin)])
def update(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)) -> dict[str, object]:
    product = service.update_product(db, product_id, data)
    return success("Product updated successfully", ProductRead.model_validate(product).model_dump(mode="json"))


@router.delete("/{product_id}", dependencies=[Depends(require_admin)])
def delete(product_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    service.delete_product(db, product_id)
    return success("Product deleted successfully", None)
