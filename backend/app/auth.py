from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.permissions import require_roles
from app.schemas import (
    Token,
    UserCreate,
    UserRead,
)
from app.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
)


router = APIRouter()


@router.post(
    "/auth/login",
    response_model=Token,
)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(
        db,
        form.username,
        form.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    token = create_access_token(user)

    return Token(
        access_token=token,
        token_type="bearer",
    )


@router.get(
    "/auth/me",
    response_model=UserRead,
)
def get_me(
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:
    return current_user


@router.post(
    "/auth/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin"),
    ),
) -> User:
    email = str(
        user_data.email,
    ).strip().lower()

    existing = db.scalar(
        select(User).where(
            User.email == email,
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        email=email,
        full_name=user_data.full_name.strip(),
        password_hash=hash_password(
            user_data.password,
        ),
        role=user_data.role.value,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user