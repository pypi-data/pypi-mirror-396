"""
Core Infinity Stones SSO Authentication Library

A library for Microsoft Single Sign-On authentication and authorization with RBAC support.
"""

from core_infinity_stones_sso.auth import MicrosoftSSOAuth
from core_infinity_stones_sso.config import Settings
from core_infinity_stones_sso.database import Database
from core_infinity_stones_sso.dependencies import (
    get_current_user,
    require_app_role,
    require_db_role,
    require_group,
    require_permission,
)
from core_infinity_stones_sso.fastapi_integration import (
    MicrosoftSSOAuthManager,
    create_auth_router,
)
from core_infinity_stones_sso.models import Permission, Role, User, get_library_metadata
from core_infinity_stones_sso.router import router as auth_router

__version__ = "0.1.0"
__all__ = [
    "MicrosoftSSOAuth",
    "Settings",
    "User",
    "Role",
    "Permission",
    "Database",
    "get_current_user",
    "require_group",
    "require_app_role",
    "require_db_role",
    "require_permission",
    "auth_router",
    "create_auth_router",
    "MicrosoftSSOAuthManager",
    "get_library_metadata",
]
