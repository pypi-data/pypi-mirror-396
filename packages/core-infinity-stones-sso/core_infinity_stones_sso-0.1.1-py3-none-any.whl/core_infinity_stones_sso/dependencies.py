"""FastAPI dependencies for authentication and authorization."""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core_infinity_stones_sso.auth import MicrosoftSSOAuth
from core_infinity_stones_sso.config import Settings
from core_infinity_stones_sso.database import Database
from core_infinity_stones_sso.models import User

security = HTTPBearer()

# Backward compatibility: Global instances for old-style usage
_settings_instance: Optional[Settings] = None
_database_instance: Optional[Database] = None


def get_settings() -> Settings:
    """Dependency to get settings (backward compatibility - uses env vars)."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings.from_env()
    return _settings_instance


def get_database(settings: Settings = Depends(get_settings)) -> Database:
    """Dependency to get database instance (backward compatibility)."""
    global _database_instance
    if _database_instance is None:
        _database_instance = Database(settings)
    return _database_instance


def get_db_session(
    database: Database = Depends(get_database),
) -> Generator[Session, None, None]:
    """Dependency to get database session (backward compatibility)."""
    yield from database.get_session()


def get_auth(settings: Settings = Depends(get_settings)) -> MicrosoftSSOAuth:
    """Dependency to get MicrosoftSSOAuth instance (backward compatibility)."""
    database = Database(settings)
    return MicrosoftSSOAuth(settings, database)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth: MicrosoftSSOAuth = Depends(get_auth),
    db: Session = Depends(get_db_session),
) -> User:
    """
    FastAPI dependency to get the current authenticated user (backward compatibility).

    Roles are extracted from the JWT token and attached to the user object.
    This ensures roles are always up-to-date and reflect current Azure AD state.
    """
    token = credentials.credentials
    payload, error_type = auth.verify_token(token)

    if payload is None:
        if error_type == "expired":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please refresh your token or log in again.",
                headers={
                    "WWW-Authenticate": "Bearer error='invalid_token', error_description='The token has expired'"
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

    user = auth.get_user_by_email(db, email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Extract groups, app_roles, and database roles/permissions from token
    groups, app_roles, _, _ = auth.extract_roles_from_token_payload(payload)
    user.set_roles_from_token(groups=groups, app_roles=app_roles)
    # Database roles are already loaded from DB via relationship

    return user


def require_group(group_name: str):
    """
    FastAPI dependency factory to require a specific Microsoft group (backward compatibility).

    Usage:
        @app.get("/admin")
        def admin_route(user: User = Depends(require_group("Administrators"))):
            return {"message": "Admin access granted"}
    """

    async def group_checker(
        user: User = Depends(get_current_user),
    ) -> User:
        if not user.has_group(group_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User is not a member of required group: {group_name}",
            )
        return user

    return group_checker


def require_app_role(role_name: str):
    """
    FastAPI dependency factory to require a specific application role (backward compatibility).

    Usage:
        @app.get("/app-admin")
        def app_admin_route(user: User = Depends(require_app_role("App.Admin"))):
            return {"message": "App admin access granted"}
    """

    async def role_checker(
        user: User = Depends(get_current_user),
    ) -> User:
        if not user.has_app_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required application role: {role_name}",
            )
        return user

    return role_checker


def require_db_role(role_name: str):
    """
    FastAPI dependency factory to require a specific database role (backward compatibility).

    Usage:
        @app.get("/editor")
        def editor_route(user: User = Depends(require_db_role("Editor"))):
            return {"message": "Editor access granted"}
    """

    async def role_checker(
        user: User = Depends(get_current_user),
    ) -> User:
        if not user.has_db_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required database role: {role_name}",
            )
        return user

    return role_checker


def require_permission(permission_name: str):
    """
    FastAPI dependency factory to require a specific permission (backward compatibility).

    Usage:
        @app.get("/manage-users")
        def manage_users_route(user: User = Depends(require_permission("user.manage"))):
            return {"message": "Can manage users"}
    """

    async def permission_checker(
        user: User = Depends(get_current_user),
    ) -> User:
        if not user.has_permission(permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required permission: {permission_name}",
            )
        return user

    return permission_checker
