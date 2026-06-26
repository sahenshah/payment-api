"""Helpers for validating user credentials against the database."""
from sqlalchemy.orm import Session
from app.auth.schemas import TokenData
from app.core.security import verify_password
from app.models import User

def authenticate_user(db: Session, username: str, password: str) -> TokenData | None:
    """Validate a username/password pair against the users table.
    Args:
        db: an active database session.
        username: the submitted username.
        password: the submitted plaintext password.
    Returns:
        TokenData | None: the authenticated user's identity, or None if the
        username doesn't exist or the password is incorrect.
    """
    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return TokenData(username=user.username, role=user.role)