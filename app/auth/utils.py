"""Helpers for validating user credentials against the database."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.schemas import TokenData
from app.core.security import verify_password, get_password_hash

# Temporary hardcoded user for testing — remove when database layer is added
FAKE_USERS = {
    "sahen": {
        "username": "sahen",
        "hashed_password": get_password_hash("testpassword123"),
        "role": "admin",
    },
    "testuser": {
        "username": "testuser", 
        "hashed_password": get_password_hash("testpassword123"),
        "role": "user",
    }
}

def authenticate_user(db: Session, username: str, password: str) -> TokenData | None:
    """Validate a username/password pair.
    
    Currently uses a hardcoded user dict for testing.
    Will be replaced with database lookup when models are added.
    """
    user = FAKE_USERS.get(username)
    if user is None or not verify_password(password, user["hashed_password"]):
        return None
    return TokenData(username=user["username"], role=user["role"])

# def authenticate_user(db: Session, username: str, password: str) -> TokenData | None:
#     """Validate a username/password pair against the `users` table.

#     Args:
#         db: an active database session.
#         username: the submitted username.
#         password: the submitted plaintext password.

#     Returns:
#         TokenData | None: the authenticated user's identity, or None if the
#         username doesn't exist or the password is incorrect.
#     """
#     row = db.execute(
#         text("SELECT username, hashed_password, role FROM users WHERE username = :username"),
#         {"username": username},
#     ).first()

#     if row is None or not verify_password(password, row.hashed_password):
#         return None

#     return TokenData(username=row.username, role=row.role)
