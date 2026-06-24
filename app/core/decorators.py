"""Custom decorators for route-level permission checking."""
import functools
from fastapi import HTTPException, status
from app.auth.schemas import TokenData

ROLE_PERMISSIONS = {
    "admin": ["transfers:write", "transfers:read", "users:read", "users:write"],
    "user": ["users:write", "users:read"],
}

def require_permission(permission: str):
    """Decorator factory that checks the current user has a required permission.
    
    Maps roles to permissions using ROLE_PERMISSIONS. In production this would
    check against a permissions table in the database.
    
    Args:
        permission: required permission string e.g. 'transfers:write'
    
    Usage:
        @router.post("/transfer")
        @require_permission("transfers:write")
        def create_transfer(current_user: TokenData = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
