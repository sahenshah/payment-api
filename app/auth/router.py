"""Authentication routes: login and the current-user dependency."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, TokenData, TokenResponse
from app.auth.utils import authenticate_user
from app.core.security import InvalidTokenError, create_access_token, create_refresh_token, verify_token
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Resolve the current user from a bearer access token.

    Args:
        token: the JWT extracted from the `Authorization: Bearer` header.

    Returns:
        TokenData: the identity of the authenticated user.

    Raises:
        HTTPException: 401 if the token is missing, invalid, expired, or not
            an access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token, token_type="access")
    except InvalidTokenError as exc:
        raise credentials_exception from exc

    username = payload.get("sub")
    role = payload.get("role")
    if username is None or role is None:
        raise credentials_exception

    return TokenData(username=username, role=role)


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Validate credentials and issue an access/refresh token pair.

    Args:
        credentials: the submitted username and password.
        db: an active database session.

    Returns:
        TokenResponse: the issued access and refresh tokens.

    Raises:
        HTTPException: 401 if the username or password is incorrect.
    """
    user = authenticate_user(db, credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": user.username, "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/me", response_model=TokenData)
def read_current_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Return the identity of the currently authenticated user.

    Args:
        current_user: injected by `get_current_user` from the bearer token.

    Returns:
        TokenData: the authenticated user's identity.
    """
    return current_user
