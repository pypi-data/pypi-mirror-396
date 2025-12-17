"""Core Microsoft SSO authentication logic."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from msal import ConfidentialClientApplication
from sqlalchemy.orm import Session

from core_infinity_stones_sso.config import Settings
from core_infinity_stones_sso.database import Database
from core_infinity_stones_sso.models import User


class MicrosoftSSOAuth:
    """Microsoft SSO authentication handler."""

    def __init__(self, settings: Settings, database: Database):
        self.settings = settings
        self.database = database
        self.msal_app = ConfidentialClientApplication(
            client_id=settings.microsoft_client_id,
            client_credential=settings.microsoft_client_secret,
            authority=settings.authority_url,
        )

    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """
        Generate Microsoft authorization URL for login.

        Returns:
            tuple: (authorization_url, state) - URL to redirect user to and state for CSRF protection
        """
        auth_url = self.msal_app.get_authorization_request_url(
            scopes=self.settings.scopes,
            redirect_uri=self.settings.microsoft_redirect_uri,
            state=state,
        )
        return auth_url, state or ""

    def acquire_token_by_authorization_code(self, code: str, state: Optional[str] = None) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from Microsoft redirect
            state: State parameter for CSRF protection

        Returns:
            dict: Token response containing access_token, id_token, etc.
        """
        result = self.msal_app.acquire_token_by_authorization_code(
            code=code,
            scopes=self.settings.scopes,
            redirect_uri=self.settings.microsoft_redirect_uri,
        )
        return result

    def extract_app_roles_from_id_token(self, id_token: str) -> list[str]:
        """
        Extract application roles from Microsoft ID token.

        Application roles are defined in Azure AD app registration and
        are returned in the ID token's 'roles' claim.

        Args:
            id_token: Microsoft ID token (JWT string)

        Returns:
            list[str]: List of application role names
        """
        try:
            # Decode the ID token without verification (it's already verified by Microsoft)
            # We just need to extract the claims
            from jose import jwt as jose_jwt

            # Decode without verification since Microsoft already signed it
            # We're just extracting the payload
            unverified = jose_jwt.get_unverified_claims(id_token)
            roles = unverified.get("roles", [])

            # Ensure it's a list
            if isinstance(roles, str):
                return [roles]
            elif isinstance(roles, list):
                return roles
            else:
                return []
        except Exception:
            # If we can't decode the token, return empty list
            return []

    def get_user_info(self, access_token: str) -> dict:
        """
        Get user information from Microsoft Graph API.

        Args:
            access_token: Microsoft access token

        Returns:
            dict: User information from Microsoft Graph
        """
        import httpx

        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.get(
            "https://graph.microsoft.com/v1.0/me",
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

    def get_user_groups(self, access_token: str) -> list[dict]:
        """
        Get user's group memberships from Microsoft Graph API.

        Args:
            access_token: Microsoft access token

        Returns:
            list[dict]: List of groups with id and displayName
        """
        import httpx

        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.get(
            "https://graph.microsoft.com/v1.0/me/memberOf",
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        # Extract groups (filter out roles if needed, or include all)
        groups = []
        for item in data.get("value", []):
            # Include both security groups and Microsoft 365 groups
            if item.get("@odata.type") in [
                "#microsoft.graph.group",
                "#microsoft.graph.securityGroup",
            ]:
                groups.append(
                    {
                        "id": item.get("id"),
                        "displayName": item.get("displayName"),
                    }
                )

        return groups

    def create_or_update_user(self, db: Session, microsoft_user_data: dict) -> User:
        """
        Create or update user in database from Microsoft user data.

        Note: Roles are NOT stored in database. They are stored in JWT token instead.

        Args:
            db: Database session
            microsoft_user_data: User data from Microsoft Graph API

        Returns:
            User: Created or updated user object
        """
        microsoft_id = microsoft_user_data.get("id")
        email = microsoft_user_data.get("mail") or microsoft_user_data.get("userPrincipalName")

        user = db.query(User).filter(User.microsoft_id == microsoft_id).first()

        if user:
            # Update existing user
            user.email = email
            user.display_name = microsoft_user_data.get("displayName")
            user.given_name = microsoft_user_data.get("givenName")
            user.surname = microsoft_user_data.get("surname")
        else:
            # Create new user
            user = User(
                microsoft_id=microsoft_id,
                email=email,
                display_name=microsoft_user_data.get("displayName"),
                given_name=microsoft_user_data.get("givenName"),
                surname=microsoft_user_data.get("surname"),
            )
            db.add(user)

        db.commit()
        db.refresh(user)
        return user

    def create_access_token(
        self,
        user: User,
        groups: list[str] | None = None,
        app_roles: list[str] | None = None,
        db: Session | None = None,
    ) -> str:
        """
        Create JWT access token for the user with groups, app_roles, and database roles.

        Args:
            user: User object
            groups: List of group names (from Microsoft)
            app_roles: List of application role names (from Microsoft)
            db: Database session (optional, needed to load database roles)

        Returns:
            str: JWT access token
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.access_token_expire_minutes
        )

        # Get database roles and permissions if db session provided
        db_role_names = []
        permission_names = []

        if db is not None:
            # Refresh user to get latest roles from database
            db.refresh(user, ["db_roles"])
            if user.db_roles:
                db_role_names = [role.name for role in user.db_roles]
                # Get permissions from roles
                for role in user.db_roles:
                    db.refresh(role, ["permissions"])
                    if role.permissions:
                        for permission in role.permissions:
                            permission_names.append(permission.name)

        to_encode = {
            "sub": user.email,
            "microsoft_id": user.microsoft_id,
            "app_roles": app_roles or [],
            "db_roles": list(set(db_role_names)),  # Remove duplicates
            "permissions": list(set(permission_names)),  # Remove duplicates
            "exp": expire,
        }

        encoded_jwt = jwt.encode(
            to_encode, self.settings.secret_key, algorithm=self.settings.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> tuple[Optional[dict], Optional[str]]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            tuple: (payload, error_type) where:
                - payload: Decoded token payload or None if invalid
                - error_type: "expired", "invalid", or None if valid
        """
        try:
            payload = jwt.decode(
                token, self.settings.secret_key, algorithms=[self.settings.algorithm]
            )
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "expired"
        except JWTError:
            return None, "invalid"

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using Microsoft refresh token.

        Args:
            refresh_token: Microsoft refresh token

        Returns:
            dict: Token response containing new access_token, id_token, etc.
        """
        result = self.msal_app.acquire_token_by_refresh_token(
            refresh_token=refresh_token,
            scopes=self.settings.scopes,
        )
        return result

    def extract_roles_from_token_payload(
        self, payload: dict
    ) -> tuple[list[str], list[str], list[str], list[str]]:
        """
        Extract groups, app_roles, and database roles/permissions from token payload.

        The token payload contains:
        - groups: List of Microsoft group names
        - app_roles: List of Microsoft application roles
        - db_roles: List of database role names
        - permissions: List of permission names

        Args:
            payload: Decoded JWT token payload

        Returns:
            tuple: (groups, app_roles, db_roles, permissions)
        """
        groups = payload.get("groups", [])
        app_roles = payload.get("app_roles", [])
        db_roles = payload.get("db_roles", [])
        permissions = payload.get("permissions", [])

        return (groups, app_roles, db_roles, permissions)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email address."""
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    def logout(self, token: str) -> bool:
        """
        Handle logout (invalidate token on client side).

        Note: For stateless JWT, logout is typically handled client-side by removing the token.
        For server-side logout, you would need to maintain a token blacklist.

        Args:
            token: JWT token to invalidate

        Returns:
            bool: True if logout successful
        """
        # In a stateless JWT system, logout is handled client-side
        # If you need server-side logout, implement a token blacklist
        return True
