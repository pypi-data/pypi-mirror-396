"""Database models for user, roles, and permissions."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Association tables for many-to-many relationships
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class User(Base):
    """
    User model representing an authenticated employee.

    Users can have:
    1. Microsoft groups and app_roles (from Azure AD, stored in JWT token)
    2. Database roles (stored in database, assigned via user_roles table)
    3. Permissions (inherited from database roles)
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    microsoft_id = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=True)
    given_name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Database roles relationship (many-to-many)
    db_roles = relationship("Role", secondary=user_roles, back_populates="users")

    def __init__(self, **kwargs):
        """Initialize user with optional role attributes from token."""
        super().__init__(**kwargs)
        # Groups and app_roles are stored in JWT token, not in database
        # These are set from token when user is authenticated
        self._token_groups: list[str] | None = None
        self._token_app_roles: list[str] | None = None

    def __repr__(self) -> str:
        return f"<User(email={self.email}, microsoft_id={self.microsoft_id})>"

    def set_roles_from_token(
        self,
        groups: list[str] | None = None,
        app_roles: list[str] | None = None,
    ) -> None:
        """
        Set groups and app_roles from JWT token. Called during authentication.

        Args:
            groups: List of group names only
            app_roles: List of application roles only
        """
        self._token_groups = groups or []
        self._token_app_roles = app_roles or []

    # Microsoft groups and app_roles methods (from token)
    def get_group_names(self) -> list[str]:
        """
        Get list of Microsoft group names from token.

        Returns:
            list[str]: List of group names from token
        """
        return self._token_groups or []

    def get_app_role_names(self) -> list[str]:
        """
        Get list of Microsoft application roles from token.

        Returns:
            list[str]: List of application role names from token
        """
        return self._token_app_roles or []

    def has_group(self, group_name: str) -> bool:
        """
        Check if user is a member of a specific Microsoft group.

        Args:
            group_name: Group display name to check

        Returns:
            bool: True if user is a member of the group
        """
        group_names = self.get_group_names()
        return group_name in group_names

    def has_any_group(self, group_names: list[str]) -> bool:
        """
        Check if user is a member of any of the specified groups.

        Args:
            group_names: List of group names to check

        Returns:
            bool: True if user is a member of any of the groups
        """
        user_groups = self.get_group_names()
        return any(group in user_groups for group in group_names)

    def has_app_role(self, role_name: str) -> bool:
        """
        Check if user has a specific Microsoft application role.

        Args:
            role_name: Application role name to check

        Returns:
            bool: True if user has the application role
        """
        app_roles = self.get_app_role_names()
        return role_name in app_roles

    def has_any_app_role(self, role_names: list[str]) -> bool:
        """
        Check if user has any of the specified application roles.

        Args:
            role_names: List of application role names to check

        Returns:
            bool: True if user has any of the application roles
        """
        user_app_roles = self.get_app_role_names()
        return any(role in user_app_roles for role in role_names)

    # Database roles and permissions methods
    def get_db_role_names(self) -> list[str]:
        """
        Get list of database role names assigned to this user.

        Returns:
            list[str]: List of database role names
        """
        return [role.name for role in self.db_roles] if self.db_roles else []

    def has_db_role(self, role_name: str) -> bool:
        """
        Check if user has a specific database role.

        Args:
            role_name: Database role name to check

        Returns:
            bool: True if user has the database role
        """
        return any(role.name == role_name for role in (self.db_roles or []))

    def has_any_db_role(self, role_names: list[str]) -> bool:
        """
        Check if user has any of the specified database roles.

        Args:
            role_names: List of database role names to check

        Returns:
            bool: True if user has any of the database roles
        """
        user_db_roles = self.get_db_role_names()
        return any(role in user_db_roles for role in role_names)

    def get_permission_names(self) -> list[str]:
        """
        Get list of all permission names from user's database roles.

        Returns:
            list[str]: List of permission names
        """
        permissions = set()
        for role in self.db_roles or []:
            for permission in role.permissions or []:
                permissions.add(permission.name)
        return list(permissions)

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if user has a specific permission (from database roles).

        Args:
            permission_name: Permission name to check

        Returns:
            bool: True if user has the permission
        """
        return permission_name in self.get_permission_names()

    def has_any_permission(self, permission_names: list[str]) -> bool:
        """
        Check if user has any of the specified permissions.

        Args:
            permission_names: List of permission names to check

        Returns:
            bool: True if user has any of the permissions
        """
        user_permissions = self.get_permission_names()
        return any(perm in user_permissions for perm in permission_names)


class Role(Base):
    """Database role model."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="db_roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role(name={self.name})>"


class Permission(Base):
    """Permission model."""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self) -> str:
        return f"<Permission(name={self.name})>"


def get_library_metadata(include_rbac: bool = False):
    """
    Get SQLAlchemy metadata for library models.

    This function allows downstream apps to selectively include
    only the models they need in their Alembic migrations.

    Args:
        include_rbac: If True, includes Role and Permission tables.
                     If False, includes only User table.

    Returns:
        MetaData object containing selected tables

    Example:
        # App 1: User only
        target_metadata = get_library_metadata(include_rbac=False)

        # App 2: User + RBAC
        target_metadata = get_library_metadata(include_rbac=True)
    """
    from sqlalchemy import MetaData

    metadata = MetaData()

    # Always include User table
    User.__table__.tometadata(metadata)

    if include_rbac:
        # Include RBAC tables
        Role.__table__.tometadata(metadata)
        Permission.__table__.tometadata(metadata)
        user_roles.tometadata(metadata)
        role_permissions.tometadata(metadata)

    return metadata
