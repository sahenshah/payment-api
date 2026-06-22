"""Pydantic models for the auth API."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Credentials submitted to the login endpoint."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Access/refresh token pair returned on successful login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Claims extracted from a verified JWT, identifying the current user."""

    username: str
    role: str
