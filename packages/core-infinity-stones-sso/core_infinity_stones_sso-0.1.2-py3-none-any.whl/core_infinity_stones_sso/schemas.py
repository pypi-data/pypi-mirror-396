"""Pydantic schemas for FastAPI request/response models."""

from typing import Optional

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Response model for token endpoint."""

    access_token: str
    token_type: str = "bearer"
    user: dict
    refresh_token: Optional[str] = None


class UserResponse(BaseModel):
    """Response model for user information."""

    microsoft_id: str
    email: str
    display_name: Optional[str]
    given_name: Optional[str]
    surname: Optional[str]
    # groups: list[str]  # Microsoft group names
    app_roles: list[str]  # Microsoft application roles
    db_roles: list[str]  # Database role names
    permissions: list[str]  # Permission names (from database roles)
