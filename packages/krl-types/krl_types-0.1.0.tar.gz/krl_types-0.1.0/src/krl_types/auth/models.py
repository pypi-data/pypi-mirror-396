# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""Authentication and authorization models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from krl_types.auth.enums import AuthProvider, TokenType, PermissionScope
from krl_types.billing import Tier


class Permission(BaseModel):
    """A single permission grant."""
    
    scope: PermissionScope
    resource_id: Optional[str] = None  # Specific resource, or None for all
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class UserTier(BaseModel):
    """User's subscription tier information."""
    
    tier: Tier
    started_at: datetime
    expires_at: Optional[datetime] = None
    is_trial: bool = False
    trial_ends_at: Optional[datetime] = None


class User(BaseModel):
    """
    Canonical user representation across the KRL platform.
    
    This is the single source of truth for user identity.
    All services MUST use this type for user representation.
    """
    
    id: UUID = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User's email address")
    display_name: str = Field(..., description="User's display name")
    
    # Authentication
    auth_provider: AuthProvider = Field(
        default=AuthProvider.LOCAL,
        description="Authentication provider used"
    )
    external_id: Optional[str] = Field(
        default=None,
        description="ID from external auth provider"
    )
    email_verified: bool = Field(
        default=False,
        description="Whether email has been verified"
    )
    
    # Subscription
    tier_info: UserTier = Field(..., description="User's subscription tier")
    
    # Organization
    organization_id: Optional[UUID] = Field(
        default=None,
        description="Organization the user belongs to"
    )
    organization_name: Optional[str] = Field(
        default=None,
        description="Organization display name"
    )
    
    # Permissions
    permissions: list[Permission] = Field(
        default_factory=list,
        description="Granted permissions"
    )
    is_admin: bool = Field(
        default=False,
        description="Platform administrator flag"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    # Usage tracking
    tcu_used_this_period: int = Field(
        default=0,
        description="TCU consumed in current billing period"
    )
    tcu_limit: int = Field(
        default=100,
        description="TCU limit for current tier"
    )
    
    def has_permission(self, scope: PermissionScope, resource_id: Optional[str] = None) -> bool:
        """Check if user has a specific permission."""
        if self.is_admin:
            return True
        for perm in self.permissions:
            if perm.scope == scope:
                if perm.resource_id is None or perm.resource_id == resource_id:
                    if perm.expires_at is None or perm.expires_at > datetime.utcnow():
                        return True
        return False
    
    def can_execute(self) -> bool:
        """Check if user can execute models (has budget and permission)."""
        return (
            self.has_permission(PermissionScope.EXECUTE_MODELS) and
            self.tcu_used_this_period < self.tcu_limit
        )


class Session(BaseModel):
    """
    User session information.
    
    Used for JWT payload and session tracking.
    """
    
    session_id: UUID = Field(..., description="Unique session identifier")
    user_id: UUID = Field(..., description="User this session belongs to")
    
    # Token info
    token_type: TokenType = Field(
        default=TokenType.ACCESS,
        description="Type of token"
    )
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Token expiration time")
    
    # Session metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_id: Optional[str] = None
    
    # Security
    is_revoked: bool = Field(
        default=False,
        description="Whether session has been revoked"
    )
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        return (
            not self.is_revoked and
            self.expires_at > datetime.utcnow()
        )


class APIKey(BaseModel):
    """
    API key for programmatic access.
    """
    
    key_id: UUID = Field(..., description="Unique key identifier")
    user_id: UUID = Field(..., description="User this key belongs to")
    
    name: str = Field(..., description="Human-readable key name")
    prefix: str = Field(..., description="Key prefix for identification (e.g., 'krl_')")
    
    # Permissions
    scopes: list[PermissionScope] = Field(
        default_factory=list,
        description="Allowed permission scopes"
    )
    
    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    # Security
    is_active: bool = Field(default=True)
    rate_limit: int = Field(
        default=1000,
        description="Requests per hour"
    )


class LicenseValidation(BaseModel):
    """
    License validation response.
    """
    
    is_valid: bool = Field(..., description="Whether license is valid")
    user_id: Optional[UUID] = Field(
        default=None,
        description="User ID if license is valid"
    )
    tier: Optional[Tier] = Field(
        default=None,
        description="Licensed tier"
    )
    
    # Validation details
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Error handling
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    # Features
    enabled_features: list[str] = Field(
        default_factory=list,
        description="Features enabled by this license"
    )
    disabled_features: list[str] = Field(
        default_factory=list,
        description="Features not available on this tier"
    )
