# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
KRL Types - Shared Type Definitions

Canonical type definitions used across the KRL Analytics Platform.
This package ensures type consistency between client SDK and server API.

Usage:
    from krl_types.billing import Tier, Money, UsageRecord
    from krl_types.billing.currency import round_currency, to_cents
"""

__version__ = "0.1.0"

# Re-export commonly used types at package root
from krl_types.billing import (
    # Enums
    Tier,
    CustomerSegment,
    ContractType,
    ContractStatus,
    PaymentTerms,
    CreditType,
    UsageMetricType,
    HealthCategory,
    ChurnRisk,
    PricingStrategy,
    ValueDriver,
    # Currency
    Currency,
    Money,
    # Models
    UsageRecord,
    TierPricing,
    BillingPeriod,
)

from krl_types.auth import (
    # Models
    User,
    Session,
    APIKey,
    LicenseValidation,
    Permission,
    UserTier,
    # Enums
    AuthProvider,
    TokenType,
    PermissionScope,
)

__all__ = [
    # Version
    "__version__",
    # Billing Enums
    "Tier",
    "CustomerSegment",
    "ContractType",
    "ContractStatus",
    "PaymentTerms",
    "CreditType",
    "UsageMetricType",
    "HealthCategory",
    "ChurnRisk",
    "PricingStrategy",
    "ValueDriver",
    # Currency
    "Currency",
    "Money",
    # Billing Models
    "UsageRecord",
    "TierPricing",
    "BillingPeriod",
    # Auth Enums
    "AuthProvider",
    "TokenType",
    "PermissionScope",
    # Auth Models
    "User",
    "Session",
    "APIKey",
    "LicenseValidation",
    "Permission",
    "UserTier",
]
