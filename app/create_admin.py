"""Create or promote an administrator: python -m app.create_admin EMAIL"""

import argparse
from getpass import getpass

import app.models  # noqa: F401
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.repositories.users import get_user_by_email


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote a coffee shop administrator")
    parser.add_argument("email")
    args = parser.parse_args()
    email = args.email.lower().strip()
    with SessionLocal() as db:
        user = get_user_by_email(db, email)
        if user is None:
            name = input("Full name: ").strip()
            password = getpass("Password (at least 8 characters): ")
            if not name or len(password) < 8 or len(password.encode()) > 72:
                parser.error("A name and password of 8 to 72 bytes are required")
            user = User(email=email, name=name, password_hash=hash_password(password))
            db.add(user)
        user.role = "ADMIN"
        user.active = True
        db.commit()
    print(f"Administrator ready: {email}")


if __name__ == "__main__":
    main()
