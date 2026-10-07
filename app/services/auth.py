from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories import users as repo
from app.schemas.user import UserCreate, UserUpdate


def register_user(db: Session, data: UserCreate) -> User:
    if repo.get_user_by_email(db, data.email):
        raise AppError("Email already registered", 409)
    user = User(name=data.name, email=data.email, password_hash=hash_password(data.password), role="CUSTOMER")
    try:
        return repo.save_user(db, user)
    except IntegrityError:
        db.rollback()
        raise AppError("Email already registered", 409) from None


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = repo.get_user_by_email(db, email.lower().strip())
    if user is None or not user.active or not verify_password(password, user.password_hash):
        raise AppError("Incorrect email or password", 401)
    return user


def list_users(db: Session) -> list[User]:
    return repo.list_users(db)


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = repo.get_user(db, user_id)
    if user is None:
        raise AppError("User not found", 404)
    changes = data.model_dump(exclude_none=True)
    for field, value in changes.items():
        setattr(user, field, value.value if field == "role" else value)
    return repo.save_user(db, user)
