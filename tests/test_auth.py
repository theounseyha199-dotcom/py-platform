from app.core.security import create_access_token, get_current_user, require_admin, require_staff
from app.schemas.user import Role, UserCreate, UserUpdate
from app.services import auth
from tests.helpers import expect_error, database_session


def test_registration_login_jwt_and_authorization() -> None:
    with database_session() as db:
        user = auth.register_user(db, UserCreate(name="Alice", email="ALICE@example.com", password="password123"))
        assert user.role == "CUSTOMER" and user.email == "alice@example.com"
        assert auth.authenticate_user(db, "alice@example.com", "password123").id == user.id
        expect_error(lambda: auth.authenticate_user(db, "alice@example.com", "wrong"), 401)
        expect_error(lambda: auth.register_user(db, UserCreate(name="Alice", email="alice@example.com", password="password123")), 409)
        token = create_access_token(user.id)
        assert get_current_user(token, db).id == user.id
        expect_error(lambda: get_current_user("invalid", db), 401)
        expect_error(lambda: require_admin(user), 403)
        user = auth.update_user(db, user.id, UserUpdate(role=Role.STAFF))
        assert require_staff(user).id == user.id
        user = auth.update_user(db, user.id, UserUpdate(active=False))
        expect_error(lambda: get_current_user(token, db), 401)
