"""Helpers for validating user credentials against the database."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.schemas import TokenData
from app.core.security import verify_password


def authenticate_user(db: Session, username: str, password: str) -> TokenData | None:
    """Validate a username/password pair against the `users` table.

    Args:
        db: an active database session.
        username: the submitted username.
        password: the submitted plaintext password.

    Returns:
        TokenData | None: the authenticated user's identity, or None if the
        username doesn't exist or the password is incorrect.
    """
    row = db.execute(
        text("SELECT username, hashed_password, role FROM users WHERE username = :username"),
        {"username": username},
    ).first()

    if row is None or not verify_password(password, row.hashed_password):
        return None

    return TokenData(username=row.username, role=row.role)
