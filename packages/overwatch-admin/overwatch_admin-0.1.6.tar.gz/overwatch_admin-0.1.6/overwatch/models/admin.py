"""
Overwatch Admin models for authentication and authorization.
"""

import enum
import json
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from overwatch.models.audit_log import AuditLog

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from overwatch.core.database import Base


class OverwatchAdminRole(str, enum.Enum):
    """Overwatch admin role enumeration."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    READ_ONLY = "read_only"


class OverwatchAdminStatus(str, enum.Enum):
    """Overwatch admin status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Admin(Base):
    """
    Overwatch Admin model for authentication and authorization.

    This is completely separate from the host application's user system.
    """

    __tablename__ = "overwatch_admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Admin information
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))

    # Role and permissions
    role: Mapped[OverwatchAdminRole] = mapped_column(
        Enum(OverwatchAdminRole), default=OverwatchAdminRole.ADMIN
    )
    status: Mapped[OverwatchAdminStatus] = mapped_column(
        Enum(OverwatchAdminStatus), default=OverwatchAdminStatus.ACTIVE
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Security fields
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Two-factor authentication
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[str | None] = mapped_column(String(255))
    backup_codes: Mapped[str | None] = mapped_column(Text)  # JSON string

    # Session management
    session_token: Mapped[str | None] = mapped_column(String(255))  # Current session
    refresh_token: Mapped[str | None] = mapped_column(
        String(255)
    )  # Current refresh token

    # Permissions (JSON field for custom permissions)
    custom_permissions: Mapped[str | None] = mapped_column(Text)  # JSON string

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by: Mapped[int | None] = mapped_column(Integer)
    updated_by: Mapped[int | None] = mapped_column(Integer)

    # Relationships
    sessions: Mapped[list["AdminSession"]] = relationship(
        "AdminSession", back_populates="admin", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="admin", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        """Get admin's full name."""
        if self.first_name and self.last_name:
            return str(f"{self.first_name} {self.last_name}")
        return str(self.username)

    @property
    def is_locked(self) -> bool:
        """Check if admin account is locked."""
        if self.locked_until is None:
            return False
        return bool(self.locked_until > datetime.now(self.locked_until.tzinfo))

    @property
    def can_login(self) -> bool:
        """Check if admin can login."""
        return bool(
            self.is_active
            and self.status == OverwatchAdminStatus.ACTIVE
            and not self.is_locked
        )

    def has_permission(self, permission: str) -> bool:
        """Check if admin has a specific permission."""
        # Super admins have all permissions
        if self.role == OverwatchAdminRole.SUPER_ADMIN:
            return True

        # Read-only admins only have read permissions
        if self.role == OverwatchAdminRole.READ_ONLY:
            return permission.startswith("read:")

        # Regular admins have standard permissions
        if self.role == OverwatchAdminRole.ADMIN:
            return True

        # Check custom permissions if set
        if self.custom_permissions:
            custom_perms = (
                str(self.custom_permissions) if self.custom_permissions else ""
            )
            try:
                permissions = json.loads(custom_perms)
                return permission in permissions.get("allowed", [])
            except (json.JSONDecodeError, AttributeError):
                pass

        return False

    def __repr__(self) -> str:
        return f"<Admin(id={self.id}, username='{self.username}', role='{self.role}')>"


class AdminSession(Base):
    """
    Admin session model for tracking active sessions.
    """

    __tablename__ = "overwatch_admin_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    admin_id: Mapped[int] = mapped_column(
        ForeignKey("overwatch_admins.id"), nullable=False, index=True
    )

    # Session information
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Request information
    ip_address: Mapped[str | None] = mapped_column(String(45))  # IPv6 compatible
    user_agent: Mapped[str | None] = mapped_column(Text)

    # Session status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    terminated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    admin: Mapped["Admin"] = relationship("Admin", back_populates="sessions")

    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return bool(datetime.now(self.expires_at.tzinfo) > self.expires_at)

    def __repr__(self) -> str:
        return f"<AdminSession(id={self.id}, admin_id={self.admin_id}, active={self.is_active})>"


class AdminPermission(Base):
    """
    Admin permission model for fine-grained permissions.
    """

    __tablename__ = "overwatch_admin_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    admin_id: Mapped[int] = mapped_column(
        ForeignKey("overwatch_admins.id"), nullable=False, index=True
    )

    # Permission details
    resource: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "User", "Product"
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., "read", "write", "delete"
    resource_id: Mapped[int | None] = mapped_column(
        Integer
    )  # Specific resource ID, null for global

    # Permission status
    is_granted: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    granted_by: Mapped[int | None] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<AdminPermission(admin_id={self.admin_id}, resource='{self.resource}', action='{self.action}')>"


# Event listeners for admin model
@event.listens_for(Admin, "before_insert")
def set_admin_defaults(mapper, connection, target):
    """Set default values for admin before insert."""
    if not target.first_name and not target.last_name:
        target.first_name = target.username


@event.listens_for(Admin, "before_update")
def update_admin_timestamp(mapper, connection, target):
    """Update timestamp when admin is modified."""
    target.updated_at = func.now()
