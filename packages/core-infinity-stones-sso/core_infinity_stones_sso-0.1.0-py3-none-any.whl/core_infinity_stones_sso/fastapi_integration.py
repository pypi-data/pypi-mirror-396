"""FastAPI integration for Microsoft SSO authentication."""

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core_infinity_stones_sso.auth import MicrosoftSSOAuth
from core_infinity_stones_sso.config import Settings
from core_infinity_stones_sso.database import Database
from core_infinity_stones_sso.manager_router import create_manager_router
from core_infinity_stones_sso.models import User

security = HTTPBearer()


class MicrosoftSSOAuthManager:
    """
    Manager class for Microsoft SSO authentication.

    Initialize this with your configuration, then use it to get FastAPI dependencies
    and router.

    Example:
        settings = Settings(
            microsoft_client_id="...",
            microsoft_client_secret="...",
            microsoft_tenant_id="...",
            microsoft_redirect_uri="...",
            database_url="...",
            secret_key="...",
        )
        auth_manager = MicrosoftSSOAuthManager(settings)
        app.include_router(auth_manager.get_router())
    """

    def __init__(self, settings: Settings):
        """
        Initialize the auth manager with settings.

        Args:
            settings: Settings instance with all required configuration
        """
        self.settings = settings
        self.database = Database(settings)
        self.auth = MicrosoftSSOAuth(settings, self.database)

    def get_db_session(self) -> Generator[Session, None, None]:
        """Dependency to get database session."""
        yield from self.database.get_session()

    def get_current_user_dependency(self):
        """Get the get_current_user dependency function."""

        async def get_current_user(
            credentials: HTTPAuthorizationCredentials = Depends(security),
            db: Session = Depends(self.get_db_session),
        ) -> User:
            """
            FastAPI dependency to get the current authenticated user.

            Roles are extracted from the JWT token and attached to the user object.
            This ensures roles are always up-to-date and reflect current Azure AD state.
            """
            token = credentials.credentials
            payload, error_type = self.auth.verify_token(token)

            if payload is None:
                if error_type == "expired":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has expired. Please refresh your token or log in again.",
                        headers={
                            "WWW-Authenticate": (
                                "Bearer error='invalid_token', "
                                "error_description='The token has expired'"
                            )
                        },
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )

            user = self.auth.get_user_by_email(db, email)
            if user is None or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive",
                )

            # Extract groups, app_roles, and database roles/permissions from token
            groups, app_roles, _, _ = self.auth.extract_roles_from_token_payload(payload)
            user.set_roles_from_token(groups=groups, app_roles=app_roles)
            # Database roles are already loaded from DB via relationship

            return user

        return get_current_user

    def require_group(self, group_name: str):
        """FastAPI dependency factory to require a specific Microsoft group."""
        get_current_user = self.get_current_user_dependency()

        async def group_checker(user: User = Depends(get_current_user)) -> User:
            if not user.has_group(group_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User is not a member of required group: {group_name}",
                )
            return user

        return group_checker

    def require_any_group(self, group_names: list[str]):
        """FastAPI dependency factory to require any of the specified groups."""
        get_current_user = self.get_current_user_dependency()

        async def group_checker(user: User = Depends(get_current_user)) -> User:
            if not user.has_any_group(group_names):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User is not a member of any of the required groups: {', '.join(group_names)}",
                )
            return user

        return group_checker

    def require_app_role(self, role_name: str):
        """FastAPI dependency factory to require a specific application role."""
        get_current_user = self.get_current_user_dependency()

        async def role_checker(user: User = Depends(get_current_user)) -> User:
            if not user.has_app_role(role_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have required application role: {role_name}",
                )
            return user

        return role_checker

    def require_any_app_role(self, role_names: list[str]):
        """FastAPI dependency factory to require any of the specified application roles."""
        get_current_user = self.get_current_user_dependency()

        async def role_checker(user: User = Depends(get_current_user)) -> User:
            if not user.has_any_app_role(role_names):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have any of the required application roles: {', '.join(role_names)}",
                )
            return user

        return role_checker

    def require_db_role(self, role_name: str):
        """FastAPI dependency factory to require a specific database role."""
        get_current_user = self.get_current_user_dependency()

        async def role_checker(user: User = Depends(get_current_user)) -> User:
            if not user.has_db_role(role_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have required database role: {role_name}",
                )
            return user

        return role_checker

    def require_any_db_role(self, role_names: list[str]):
        """FastAPI dependency factory to require any of the specified database roles."""
        get_current_user = self.get_current_user_dependency()

        async def role_checker(user: User = Depends(get_current_user)) -> User:
            if not user.has_any_db_role(role_names):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have any of the required database roles: {', '.join(role_names)}",
                )
            return user

        return role_checker

    def require_permission(self, permission_name: str):
        """FastAPI dependency factory to require a specific permission."""
        get_current_user = self.get_current_user_dependency()

        async def permission_checker(user: User = Depends(get_current_user)) -> User:
            if not user.has_permission(permission_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have required permission: {permission_name}",
                )
            return user

        return permission_checker

    def require_any_permission(self, permission_names: list[str]):
        """FastAPI dependency factory to require any of the specified permissions."""
        get_current_user = self.get_current_user_dependency()

        async def permission_checker(user: User = Depends(get_current_user)) -> User:
            if not user.has_any_permission(permission_names):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have any of the required permissions: {', '.join(permission_names)}",
                )
            return user

        return permission_checker

    def get_router(self) -> APIRouter:
        """Get the FastAPI router with all auth endpoints."""
        return create_manager_router(self)


def create_auth_router(settings: Settings) -> APIRouter:
    """
    Create an auth router with the given settings.

    This is a convenience function that creates a MicrosoftSSOAuthManager
    and returns its router.

    Args:
        settings: Settings instance with all required configuration

    Returns:
        APIRouter: FastAPI router with auth endpoints
    """
    manager = MicrosoftSSOAuthManager(settings)
    return manager.get_router()
