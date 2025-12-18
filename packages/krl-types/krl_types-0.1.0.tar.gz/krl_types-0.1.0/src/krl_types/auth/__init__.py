# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
KRL Types - Authentication and Authorization Types

Canonical type definitions for user identity, sessions, and permissions
across the KRL Analytics Platform.

Usage:
    from krl_types.auth import User, Session, APIKey, LicenseValidation
"""

from krl_types.auth.models import (
    User,
    Session,
    APIKey,
    LicenseValidation,
    Permission,
    UserTier,
)
from krl_types.auth.enums import (
    AuthProvider,
    TokenType,
    PermissionScope,
)

__all__ = [
    # Models
    "User",
    "Session",
    "APIKey",
    "LicenseValidation",
    "Permission",
    "UserTier",
    # Enums
    "AuthProvider",
    "TokenType",
    "PermissionScope",
]
