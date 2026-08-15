from fastapi import Depends, HTTPException, status

from app.models import ModelRecord, User
from app.security import get_current_user


def require_roles(*allowed_roles: str):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker


def ensure_model_owner_or_admin(
    model: ModelRecord,
    current_user: User,
) -> None:
    if current_user.role == "admin":
        return

    owns_model = (
        current_user.role == "model_owner"
        and model.owner_email.lower()
        == current_user.email.lower()
    )

    if owns_model:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to manage this model",
    )


def ensure_lifecycle_permission(
    model: ModelRecord,
    action: str,
    current_user: User,
) -> None:
    if current_user.role == "admin":
        return

    owns_model = (
        current_user.role == "model_owner"
        and model.owner_email.lower()
        == current_user.email.lower()
    )

    if action in {
        "submit_for_review",
        "retire",
    } and owns_model:
        return

    if (
        action in {
            "approve",
            "reject",
        }
        and current_user.role == "reviewer"
    ):
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to perform this lifecycle action",
    )