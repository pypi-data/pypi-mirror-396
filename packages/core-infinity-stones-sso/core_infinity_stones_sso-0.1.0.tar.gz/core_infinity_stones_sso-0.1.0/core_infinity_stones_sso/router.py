"""FastAPI router with authentication endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core_infinity_stones_sso.auth import MicrosoftSSOAuth
from core_infinity_stones_sso.dependencies import get_auth, get_current_user, get_db_session
from core_infinity_stones_sso.models import User
from core_infinity_stones_sso.schemas import TokenResponse, UserResponse

# FastAPI Router for authentication endpoints (backward compatibility)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login")
async def login(
    request: Request,
    auth: MicrosoftSSOAuth = Depends(get_auth),
    state: Optional[str] = None,
):
    """
    Initiate Microsoft SSO login flow.

    Redirects user to Microsoft login page.
    """
    auth_url, state_value = auth.get_authorization_url(state=state)
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(
    request: Request,
    code: str,
    state: Optional[str] = None,
    auth: MicrosoftSSOAuth = Depends(get_auth),
    db: Session = Depends(get_db_session),
):
    """
    Handle Microsoft OAuth callback.

    Exchanges authorization code for tokens and creates/updates user.
    Fetches user groups from Microsoft Graph and application roles from ID token.
    Stores both and returns JWT access token.
    """
    # Exchange code for token
    token_result = auth.acquire_token_by_authorization_code(code, state)

    if "error" in token_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {token_result.get('error_description')}",
        )

    # Get user info and groups from Microsoft Graph
    access_token = token_result.get("access_token")
    id_token = token_result.get("id_token", "")

    user_info = auth.get_user_info(access_token)
    user_groups = auth.get_user_groups(access_token)

    # Extract application roles from ID token
    app_roles = auth.extract_app_roles_from_id_token(id_token) if id_token else []

    # Extract group names
    group_names = [
        group.get("displayName", "") for group in user_groups if group.get("displayName")
    ]

    # Create or update user in database (without storing roles)
    user = auth.create_or_update_user(db, user_info)

    # Generate JWT token with groups and app_roles separately
    jwt_token = auth.create_access_token(user, groups=group_names, app_roles=app_roles, db=db)

    # Get refresh token from Microsoft token result
    refresh_token = token_result.get("refresh_token")

    # In a real application, you might want to redirect to frontend with token
    # For now, return JSON response
    return TokenResponse(
        access_token=jwt_token,
        user={
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "groups": group_names,
            "app_roles": app_roles,
        },
        refresh_token=refresh_token,
    )


@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    auth: MicrosoftSSOAuth = Depends(get_auth),
):
    """
    Logout endpoint.

    Note: With stateless JWT, logout is handled client-side by removing the token.
    """
    # In a stateless JWT system, logout is handled client-side
    # If you need server-side logout, implement a token blacklist here
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Returns user details including Microsoft groups, app roles, database roles, and permissions.
    """
    return UserResponse(
        email=user.email,
        display_name=user.display_name,
        given_name=user.given_name,
        surname=user.surname,
        microsoft_id=user.microsoft_id,
        app_roles=user.get_app_role_names(),
        db_roles=user.get_db_role_names(),
        permissions=user.get_permission_names(),
    )
