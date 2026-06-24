"""Authentication routes: login and the current-user dependency."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, RefreshRequest, TokenData, TokenResponse
from app.auth.utils import authenticate_user
from app.core.security import InvalidTokenError, create_access_token, create_refresh_token, verify_token
from app.database import get_db
from app.core.decorators import require_permission

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> TokenData:
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
        payload = verify_token(credentials.credentials, token_type="access")
    except InvalidTokenError as exc:
        raise credentials_exception from exc

    username = payload.get("sub")
    role = payload.get("role")
    if username is None or role is None:
        raise credentials_exception

    return TokenData(username=username, role=role)

def require_role(required_role: str):
    """Dependency to enforce that the current user has a specific role.

    Args:
        required_role: the role required to access the endpoint.

    Returns:
        A dependency function that raises an HTTPException if the user does not have the required role.
    """
    def role_dependency(current_user: TokenData = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions",
            )
        return current_user
    return role_dependency

@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest, 
    db: Session = Depends(get_db)
) -> TokenResponse:
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

@router.get("/admin-only")
def admin_only(current_user: TokenData = Depends(require_role("admin"))):
    """Test endpoint restricted to admin users only."""
    return {"message": f"Welcome admin {current_user.username}"}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_request: RefreshRequest) -> TokenResponse:
    """Validate a refresh token and issue a new access token.

    Note: refresh token rotation (invalidating the old token) will be added
    when the database layer is implemented.

    Args:
        refresh_request: the submitted refresh token.
    Returns:
        TokenResponse: the newly issued access and refresh tokens.
    Raises:
        HTTPException: 401 if the refresh token is missing, invalid, expired, or not
            a refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(refresh_request.refresh_token, token_type="refresh")
    except InvalidTokenError as exc:
        raise credentials_exception from exc

    username = payload.get("sub")
    role = payload.get("role")
    if username is None or role is None:
        raise credentials_exception

    token_data = {"sub": username, "role": role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )

@router.get("/transfer-test")
@require_permission("transfers:write")
async def transfer_test(current_user: TokenData = Depends(get_current_user)):
    """Test endpoint for require_permission decorator."""
    return {"message": f"Transfer permission granted for {current_user.username}"}