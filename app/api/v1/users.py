from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import success
from app.core.security import require_admin
from app.schemas.user import UserRead, UserUpdate
from app.services import auth as service


router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_admin)])


@router.get("")
def list_all(db: Session = Depends(get_db)) -> dict[str, object]:
    data = [UserRead.model_validate(user).model_dump(mode="json") for user in service.list_users(db)]
    return success("Users retrieved successfully", data)


@router.patch("/{user_id}")
def update(user_id: int, data: UserUpdate, db: Session = Depends(get_db)) -> dict[str, object]:
    user = service.update_user(db, user_id, data)
    return success("User updated successfully", UserRead.model_validate(user).model_dump(mode="json"))
