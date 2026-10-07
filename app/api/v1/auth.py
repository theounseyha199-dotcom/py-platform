from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import success
from app.core.security import create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserRead
from app.services import auth as service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)) -> dict[str, object]:
    user = service.register_user(db, data)
    return success("Registration successful", UserRead.model_validate(user).model_dump(mode="json"))


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict[str, object]:
    user = service.authenticate_user(db, form.username, form.password)
    return success("Login successful", Token(access_token=create_access_token(user.id)).model_dump())


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict[str, object]:
    return success("User retrieved successfully", UserRead.model_validate(user).model_dump(mode="json"))
