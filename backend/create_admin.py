from getpass import getpass

from sqlalchemy import select

from app.database import SessionLocal
from app.models import User
from app.security import hash_password


def main():
    email = input(
        "Admin email: "
    ).strip().lower()

    full_name = input(
        "Admin name: "
    ).strip()

    password = getpass(
        "Admin password: "
    )

    if len(password) < 8:
        raise ValueError(
            "Password must be at least 8 characters"
        )

    with SessionLocal() as db:
        existing = db.scalar(
            select(User).where(
                User.email == email,
            )
        )

        if existing is not None:
            raise ValueError(
                "A user with that email already exists"
            )

        user = User(
            email=email,
            full_name=full_name,
            password_hash=hash_password(
                password,
            ),
            role="admin",
        )

        db.add(user)
        db.commit()

        print(
            f"Created admin user: {email}"
        )


if __name__ == "__main__":
    main()
    