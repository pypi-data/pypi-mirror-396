"""FastAPI router for MicrosoftSSOAuthManager."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core_infinity_stones_sso.models import User
from core_infinity_stones_sso.schemas import TokenResponse, UserResponse


def create_manager_router(manager):
    """
    Create router for MicrosoftSSOAuthManager.

    Args:
        manager: MicrosoftSSOAuthManager instance

    Returns:
        APIRouter: FastAPI router with auth endpoints
    """
    router = APIRouter(prefix="/auth", tags=["authentication"])
    get_current_user = manager.get_current_user_dependency()

    @router.get("/login")
    async def login(request: Request, state: Optional[str] = None):
        """Initiate Microsoft SSO login flow."""
        auth_url, state_value = manager.auth.get_authorization_url(state=state)
        return RedirectResponse(url=auth_url)

    @router.get("/callback")
    async def callback(
        request: Request,
        code: str,
        state: Optional[str] = None,
        db: Session = Depends(manager.get_db_session),
    ):
        """
        Handle Microsoft OAuth callback.

        Supports two response modes:
        - "json": Returns JSON with token and user data (default, for API usage)
        - "redirect": Redirects to frontend_redirect_uri with token in URL hash (for SPA usage)
        """
        token_result = manager.auth.acquire_token_by_authorization_code(code, state)

        if "error" in token_result:
            error_msg = token_result.get("error_description", "Authentication failed")

            # If redirect mode, redirect to frontend with error
            if (
                manager.settings.callback_response_mode == "redirect"
                and manager.settings.frontend_redirect_uri
            ):
                from urllib.parse import quote

                return RedirectResponse(
                    url=f"{manager.settings.frontend_redirect_uri}?error={quote(error_msg)}"
                )

            # Otherwise raise HTTP exception
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication failed: {error_msg}",
            )

        access_token = token_result.get("access_token")
        id_token = token_result.get("id_token", "")

        user_info = manager.auth.get_user_info(access_token)
        user_groups = manager.auth.get_user_groups(access_token)

        app_roles = manager.auth.extract_app_roles_from_id_token(id_token) if id_token else []
        group_names = [
            group.get("displayName", "") for group in user_groups if group.get("displayName")
        ]

        user = manager.auth.create_or_update_user(db, user_info)

        jwt_token = manager.auth.create_access_token(
            user, groups=group_names, app_roles=app_roles, db=db
        )

        # Get refresh token from Microsoft token result
        refresh_token = token_result.get("refresh_token")

        # Redirect mode: redirect to frontend with token in URL hash
        if (
            manager.settings.callback_response_mode == "redirect"
            and manager.settings.frontend_redirect_uri
        ):
            from urllib.parse import quote

            redirect_url = (
                f"{manager.settings.frontend_redirect_uri}#token={quote(jwt_token, safe='')}"
            )
            # Include refresh token in hash if available
            if refresh_token:
                redirect_url += f"&refresh_token={quote(refresh_token, safe='')}"
            return RedirectResponse(url=redirect_url)

        # JSON mode: return token and user data (default)
        return TokenResponse(
            access_token=jwt_token,
            user={
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "groups": group_names,
                "app_roles": app_roles,
                "db_roles": user.get_db_role_names(),
                "permissions": user.get_permission_names(),
            },
            refresh_token=refresh_token,
        )

    @router.post("/refresh")
    async def refresh_token(
        request: Request,
        db: Session = Depends(manager.get_db_session),
    ):
        """
        Refresh access token using Microsoft refresh token.

        Request body should contain:
        {
            "refresh_token": "microsoft_refresh_token_here"
        }

        Returns new access token and user information.
        """
        from pydantic import BaseModel as PydanticBaseModel

        class RefreshTokenRequest(PydanticBaseModel):
            refresh_token: str

        try:
            body = await request.json()
            refresh_request = RefreshTokenRequest(**body)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request body. Expected {'refresh_token': '...'}",
            )

        # Refresh token with Microsoft
        token_result = manager.auth.refresh_access_token(refresh_request.refresh_token)

        if "error" in token_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token refresh failed: {token_result.get('error_description')}",
            )

        # Get user info and groups from Microsoft Graph
        access_token = token_result.get("access_token")
        id_token = token_result.get("id_token", "")
        refresh_token_new = token_result.get("refresh_token")  # May or may not be present

        user_info = manager.auth.get_user_info(access_token)
        user_groups = manager.auth.get_user_groups(access_token)

        # Extract application roles from ID token
        app_roles = manager.auth.extract_app_roles_from_id_token(id_token) if id_token else []
        group_names = [
            group.get("displayName", "") for group in user_groups if group.get("displayName")
        ]

        # Create or update user
        user = manager.auth.create_or_update_user(db, user_info)

        # Generate new JWT token
        jwt_token = manager.auth.create_access_token(
            user, groups=group_names, app_roles=app_roles, db=db
        )

        response_data = {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "groups": group_names,
                "app_roles": app_roles,
                "db_roles": user.get_db_role_names(),
                "permissions": user.get_permission_names(),
            },
        }

        # Include refresh token if Microsoft provided a new one
        if refresh_token_new:
            response_data["refresh_token"] = refresh_token_new

        return response_data

    @router.post("/logout")
    async def logout(user: User = Depends(get_current_user)):
        """Logout endpoint.

        Note: With stateless JWT, logout is handled client-side by removing the token.
        """
        # In a stateless JWT system, logout is handled client-side
        # If you need server-side logout, implement a token blacklist here
        return {"message": "Logged out successfully"}

    @router.get("/me", response_model=UserResponse)
    async def get_current_user_info(user: User = Depends(get_current_user)):
        """Get current authenticated user information."""
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

    return router
