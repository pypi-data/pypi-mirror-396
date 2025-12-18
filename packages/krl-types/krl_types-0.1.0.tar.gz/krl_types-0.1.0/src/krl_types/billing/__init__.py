# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
KRL Types - Billing Module

Shared billing type definitions for client/server interoperability.
"""

from krl_types.billing.enums import (
    # Core
    Tier,
    CustomerSegment,
    # Contracts
    ContractType,
    ContractStatus,
    PaymentTerms,
    # Credits & Usage
    CreditType,
    UsageMetricType,
    # Health & Risk
    HealthCategory,
    ChurnRisk,
    InterventionType,
    # Pricing & Experiments
    PricingStrategy,
    ExperimentStatus,
    ExperimentType,
    ValueDriver,
    RiskPricingFactor,
    UpsellTriggerType,
    RevenueEventType,
    # Audit
    AuditAction,
    ActorType,
    # Stripe
    StripeSyncStatus,
    StripeEntityType,
    # Deprecated aliases
    BillingTier,
    KRLTier,
    PricingTier,
)

from krl_types.billing.currency import (
    # Classes
    Currency,
    Money,
    InvoiceLineItem,
    # Functions
    round_currency,
    to_cents,
    from_cents,
    safe_decimal,
    apply_percentage,
    apply_discount,
    format_currency,
    # Convenience constructors
    usd,
    eur,
    gbp,
    # Constants
    TWO_PLACES,
    FOUR_PLACES,
    ZERO,
    ONE,
    HUNDRED,
    # Exceptions
    CurrencyError,
    InvalidAmountError,
    CurrencyMismatchError,
)

from krl_types.billing.models import (
    UsageRecord,
    TierPricing,
    BillingPeriod,
    UpsellTrigger,
    UpsellEvent,
    RiskPricingProfile,
)

__all__ = [
    # === Enums ===
    # Core
    "Tier",
    "CustomerSegment",
    # Contracts
    "ContractType",
    "ContractStatus",
    "PaymentTerms",
    # Credits & Usage
    "CreditType",
    "UsageMetricType",
    # Health & Risk
    "HealthCategory",
    "ChurnRisk",
    "InterventionType",
    # Pricing & Experiments
    "PricingStrategy",
    "ExperimentStatus",
    "ExperimentType",
    "ValueDriver",
    "RiskPricingFactor",
    "UpsellTriggerType",
    "RevenueEventType",
    # Audit
    "AuditAction",
    "ActorType",
    # Stripe
    "StripeSyncStatus",
    "StripeEntityType",
    # Deprecated aliases
    "BillingTier",
    "KRLTier",
    "PricingTier",
    # === Currency ===
    "Currency",
    "Money",
    "InvoiceLineItem",
    "round_currency",
    "to_cents",
    "from_cents",
    "safe_decimal",
    "apply_percentage",
    "apply_discount",
    "format_currency",
    "usd",
    "eur",
    "gbp",
    "TWO_PLACES",
    "FOUR_PLACES",
    "ZERO",
    "ONE",
    "HUNDRED",
    "CurrencyError",
    "InvalidAmountError",
    "CurrencyMismatchError",
    # === Models ===
    "UsageRecord",
    "TierPricing",
    "BillingPeriod",
    "UpsellTrigger",
    "UpsellEvent",
    "RiskPricingProfile",
]
