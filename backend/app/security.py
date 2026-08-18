from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
)

from jwt.exceptions import (
    InvalidTokenError,
)

from pwdlib import PasswordHash

from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User


JWT_SECRET_KEY = (
    settings.jwt_secret_key
    .get_secret_value()
)

ALGORITHM = settings.jwt_algorithm

ACCESS_TOKEN_EXPIRE_MINUTES = (
    settings.access_token_expire_minutes
)


password_hash = (
    PasswordHash.recommended()
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def hash_password(
    password: str,
) -> str:
    return password_hash.hash(
        password
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user: User,
) -> str:
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=(
                ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    from sqlalchemy import select

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    if not user.is_active:
        return None

    return user


def get_current_user(
    token: str = Depends(
        oauth2_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = (
        HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Could not validate credentials"
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )
    )

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        try:
            user_id = int(subject)
        except (
            TypeError,
            ValueError,
        ):
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = db.get(
        User,
        user_id,
    )

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="Inactive user",
        )

    return user