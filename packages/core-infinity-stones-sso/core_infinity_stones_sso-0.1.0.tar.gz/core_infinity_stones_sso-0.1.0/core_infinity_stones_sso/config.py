"""Configuration settings for Microsoft SSO authentication."""

from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseModel):
    """
    Application settings for Microsoft SSO authentication.

    Initialize with explicit parameters for use in compiled packages.

    Example (API-only usage):
        settings = Settings(
            microsoft_client_id="...",
            microsoft_client_secret="...",
            microsoft_tenant_id="...",
            microsoft_redirect_uri="http://localhost:8000/auth/callback",
            database_url="...",
            secret_key="...",
        )

    Example (SPA/React frontend usage):
        settings = Settings(
            microsoft_client_id="...",
            microsoft_client_secret="...",
            microsoft_tenant_id="...",
            microsoft_redirect_uri="http://localhost:8000/auth/callback",
            database_url="...",
            secret_key="...",
            frontend_redirect_uri="http://localhost:3000/callback",
            callback_response_mode="redirect",
        )
    """

    # Microsoft Azure AD Configuration
    microsoft_client_id: str
    microsoft_client_secret: str
    microsoft_tenant_id: str
    microsoft_redirect_uri: str
    microsoft_authority: Optional[str] = None

    # Database Configuration
    database_url: str

    # JWT Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application Configuration
    app_name: str = "Microsoft SSO Auth"

    # Frontend redirect configuration (for SPA/React apps)
    frontend_redirect_uri: Optional[str] = None
    """
    Frontend redirect URI for callback responses.

    When set, the callback will redirect to this URI with the token in the URL hash.
    Example: "http://localhost:3000/callback"

    If None, callback returns JSON response (default for API usage).
    """
    callback_response_mode: str = "json"
    """
    Callback response mode: "json" or "redirect".

    - "json": Returns JSON response with token and user data (default, for API usage)
    - "redirect": Redirects to frontend_redirect_uri with token in URL hash (for SPA usage)

    Requires frontend_redirect_uri to be set when using "redirect" mode.
    """

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create Settings from environment variables or .env file.

        This is primarily for database migrations (Alembic) that need database_url.
        For application usage, prefer explicit parameters.
        """

        class EnvSettings(BaseSettings):
            microsoft_client_id: str
            microsoft_client_secret: str
            microsoft_tenant_id: str
            microsoft_redirect_uri: str
            microsoft_authority: Optional[str] = None
            database_url: str
            secret_key: str
            algorithm: str = "HS256"
            access_token_expire_minutes: int = 30
            app_name: str = "Microsoft SSO Auth"
            frontend_redirect_uri: Optional[str] = None
            callback_response_mode: str = "json"

            model_config = SettingsConfigDict(
                env_file=".env",
                case_sensitive=False,
            )

        env_settings = EnvSettings()
        return cls(
            microsoft_client_id=env_settings.microsoft_client_id,
            microsoft_client_secret=env_settings.microsoft_client_secret,
            microsoft_tenant_id=env_settings.microsoft_tenant_id,
            microsoft_redirect_uri=env_settings.microsoft_redirect_uri,
            microsoft_authority=env_settings.microsoft_authority,
            database_url=env_settings.database_url,
            secret_key=env_settings.secret_key,
            algorithm=env_settings.algorithm,
            access_token_expire_minutes=env_settings.access_token_expire_minutes,
            app_name=env_settings.app_name,
            frontend_redirect_uri=env_settings.frontend_redirect_uri,
            callback_response_mode=env_settings.callback_response_mode,
        )

    @property
    def authority_url(self) -> str:
        """Get the Microsoft authority URL."""
        if self.microsoft_authority:
            return self.microsoft_authority
        return f"https://login.microsoftonline.com/{self.microsoft_tenant_id}"

    @property
    def scopes(self) -> list[str]:
        """
        Get the required Microsoft Graph API scopes.

        Note: MSAL automatically adds 'openid' and 'profile' to scopes,
        so we don't include them here to avoid the "reserved scope" error.
        """
        return [
            "User.Read",
            "GroupMember.Read.All",  # To read user's group memberships
            "email",
            # "offline_access",  # Request refresh token
        ]
