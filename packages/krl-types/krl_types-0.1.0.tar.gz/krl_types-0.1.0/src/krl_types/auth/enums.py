# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""Authentication and authorization enumerations."""

from enum import Enum


class AuthProvider(str, Enum):
    """Supported authentication providers."""
    
    LOCAL = "local"
    GITHUB = "github"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    SAML = "saml"
    OIDC = "oidc"


class TokenType(str, Enum):
    """JWT token types."""
    
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"
    LICENSE = "license"


class PermissionScope(str, Enum):
    """Permission scopes for API access."""
    
    # Read operations
    READ_MODELS = "read:models"
    READ_CONNECTORS = "read:connectors"
    READ_ANALYTICS = "read:analytics"
    READ_BILLING = "read:billing"
    
    # Write operations
    WRITE_MODELS = "write:models"
    WRITE_CONNECTORS = "write:connectors"
    WRITE_ANALYTICS = "write:analytics"
    
    # Execute operations
    EXECUTE_MODELS = "execute:models"
    EXECUTE_TRAINING = "execute:training"
    EXECUTE_CONNECTORS = "execute:connectors"
    
    # Admin operations
    ADMIN_USERS = "admin:users"
    ADMIN_BILLING = "admin:billing"
    ADMIN_PLATFORM = "admin:platform"
