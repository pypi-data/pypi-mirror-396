# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Billing Data Models - Shared Dataclasses.

Pure data structures for billing entities used by both client SDK
and server API. No business logic, no I/O dependencies.

Usage:
    from krl_types.billing.models import UsageRecord, TierPricing, BillingPeriod
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set

from krl_types.billing.enums import (
    Tier,
    UsageMetricType,
    UpsellTriggerType,
    RiskPricingFactor,
)


# =============================================================================
# Usage Records
# =============================================================================

@dataclass
class UsageRecord:
    """A single usage record for billing."""
    record_id: str
    tenant_id: str
    metric_type: UsageMetricType
    quantity: Decimal
    timestamp: datetime
    
    # Billing context
    tier: Tier
    unit_price: Decimal = Decimal("0")
    total_price: Decimal = Decimal("0")
    
    # Source tracing
    source: str = ""
    correlation_id: Optional[str] = None
    
    # Risk adjustment
    risk_multiplier: Decimal = Decimal("1.0")
    risk_factors: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "tenant_id": self.tenant_id,
            "metric_type": self.metric_type.value,
            "quantity": str(self.quantity),
            "timestamp": self.timestamp.isoformat(),
            "tier": self.tier.value,
            "unit_price": str(self.unit_price),
            "total_price": str(self.total_price),
            "risk_multiplier": str(self.risk_multiplier),
            "source": self.source,
            "correlation_id": self.correlation_id,
            "risk_factors": self.risk_factors,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageRecord":
        """Create from dictionary."""
        return cls(
            record_id=data["record_id"],
            tenant_id=data["tenant_id"],
            metric_type=UsageMetricType(data["metric_type"]),
            quantity=Decimal(data["quantity"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            tier=Tier(data["tier"]),
            unit_price=Decimal(data.get("unit_price", "0")),
            total_price=Decimal(data.get("total_price", "0")),
            source=data.get("source", ""),
            correlation_id=data.get("correlation_id"),
            risk_multiplier=Decimal(data.get("risk_multiplier", "1.0")),
            risk_factors=data.get("risk_factors", {}),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Tier Pricing Configuration
# =============================================================================

@dataclass
class TierPricing:
    """Pricing configuration for a tier."""
    tier: Tier
    base_price: Decimal
    included_units: Dict[UsageMetricType, int]
    overage_rates: Dict[UsageMetricType, Decimal]
    
    # Limits
    hard_limits: Dict[UsageMetricType, int] = field(default_factory=dict)
    soft_limits: Dict[UsageMetricType, int] = field(default_factory=dict)
    
    # Risk pricing
    risk_pricing_enabled: bool = False
    max_risk_multiplier: Decimal = Decimal("2.0")
    
    # Features
    features: Set[str] = field(default_factory=set)
    ml_models_allowed: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier.value,
            "base_price": str(self.base_price),
            "included_units": {k.value: v for k, v in self.included_units.items()},
            "overage_rates": {k.value: str(v) for k, v in self.overage_rates.items()},
            "hard_limits": {k.value: v for k, v in self.hard_limits.items()},
            "soft_limits": {k.value: v for k, v in self.soft_limits.items()},
            "risk_pricing_enabled": self.risk_pricing_enabled,
            "max_risk_multiplier": str(self.max_risk_multiplier),
            "features": list(self.features),
            "ml_models_allowed": list(self.ml_models_allowed),
        }


# =============================================================================
# Billing Period
# =============================================================================

@dataclass
class BillingPeriod:
    """A billing period with accumulated usage."""
    period_id: str
    tenant_id: str
    tier: Tier
    
    start_date: datetime
    end_date: datetime
    
    # Usage
    usage: Dict[UsageMetricType, Decimal] = field(default_factory=dict)
    usage_records: List[str] = field(default_factory=list)  # record IDs
    
    # Pricing
    base_charge: Decimal = Decimal("0")
    overage_charges: Dict[UsageMetricType, Decimal] = field(default_factory=dict)
    risk_adjustments: Decimal = Decimal("0")
    discounts: Decimal = Decimal("0")
    total_charge: Decimal = Decimal("0")
    
    # Status
    finalized: bool = False
    invoiced: bool = False
    
    def compute_total(self) -> Decimal:
        """Compute total charge for the period."""
        self.total_charge = (
            self.base_charge
            + sum(self.overage_charges.values(), Decimal("0"))
            + self.risk_adjustments
            - self.discounts
        )
        return self.total_charge
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_id": self.period_id,
            "tenant_id": self.tenant_id,
            "tier": self.tier.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "usage": {k.value: str(v) for k, v in self.usage.items()},
            "usage_records": self.usage_records,
            "base_charge": str(self.base_charge),
            "overage_charges": {k.value: str(v) for k, v in self.overage_charges.items()},
            "risk_adjustments": str(self.risk_adjustments),
            "discounts": str(self.discounts),
            "total_charge": str(self.total_charge),
            "finalized": self.finalized,
            "invoiced": self.invoiced,
        }


# =============================================================================
# Upsell Configuration
# =============================================================================

@dataclass
class UpsellTrigger:
    """Configuration for an upsell trigger."""
    trigger_id: str
    trigger_type: UpsellTriggerType
    name: str
    description: str
    
    # Conditions
    source_tier: Tier
    target_tier: Tier
    condition: Dict[str, Any]
    
    # Timing
    cooldown_hours: int = 24
    max_triggers_per_month: int = 3
    
    # Messaging
    message_template: str = ""
    cta_url: str = ""
    
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_id": self.trigger_id,
            "trigger_type": self.trigger_type.value,
            "name": self.name,
            "description": self.description,
            "source_tier": self.source_tier.value,
            "target_tier": self.target_tier.value,
            "condition": self.condition,
            "cooldown_hours": self.cooldown_hours,
            "max_triggers_per_month": self.max_triggers_per_month,
            "message_template": self.message_template,
            "cta_url": self.cta_url,
            "enabled": self.enabled,
        }


@dataclass
class UpsellEvent:
    """A triggered upsell event."""
    event_id: str
    trigger_id: str
    tenant_id: str
    timestamp: datetime
    
    trigger_type: UpsellTriggerType
    source_tier: Tier
    target_tier: Tier
    
    # Context
    trigger_context: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    cta_url: str = ""
    
    # Tracking
    viewed: bool = False
    clicked: bool = False
    converted: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "trigger_id": self.trigger_id,
            "tenant_id": self.tenant_id,
            "timestamp": self.timestamp.isoformat(),
            "trigger_type": self.trigger_type.value,
            "source_tier": self.source_tier.value,
            "target_tier": self.target_tier.value,
            "trigger_context": self.trigger_context,
            "message": self.message,
            "cta_url": self.cta_url,
            "viewed": self.viewed,
            "clicked": self.clicked,
            "converted": self.converted,
        }


# =============================================================================
# Risk Pricing
# =============================================================================

@dataclass
class RiskPricingProfile:
    """Risk-based pricing profile for a tenant."""
    tenant_id: str
    
    # Current risk scores (0-1)
    dls_score: float = 1.0  # Higher is better (less risk)
    threat_score: float = 0.0  # Higher is worse
    anomaly_score: float = 0.0
    violation_score: float = 0.0
    
    # Computed multiplier
    risk_multiplier: Decimal = Decimal("1.0")
    
    # History
    score_history: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def compute_multiplier(
        self,
        weights: Dict[RiskPricingFactor, float],
        max_multiplier: Decimal = Decimal("2.0"),
    ) -> Decimal:
        """Compute risk multiplier from scores."""
        # Base: start at 1.0
        multiplier = 1.0
        
        # DLS: higher is better, so inverse contribution
        if RiskPricingFactor.DLS_SCORE in weights:
            # DLS 1.0 = no increase, DLS 0.5 = increase
            dls_penalty = (1.0 - self.dls_score) * weights[RiskPricingFactor.DLS_SCORE]
            multiplier += dls_penalty
        
        # Threat score: higher is worse
        if RiskPricingFactor.THREAT_FREQUENCY in weights:
            multiplier += self.threat_score * weights[RiskPricingFactor.THREAT_FREQUENCY]
        
        # Anomaly score
        if RiskPricingFactor.ANOMALY_RATE in weights:
            multiplier += self.anomaly_score * weights[RiskPricingFactor.ANOMALY_RATE]
        
        # Violation score
        if RiskPricingFactor.VIOLATION_HISTORY in weights:
            multiplier += self.violation_score * weights[RiskPricingFactor.VIOLATION_HISTORY]
        
        # Cap at max
        self.risk_multiplier = min(Decimal(str(multiplier)), max_multiplier)
        self.last_updated = datetime.now()
        
        return self.risk_multiplier
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "dls_score": self.dls_score,
            "threat_score": self.threat_score,
            "anomaly_score": self.anomaly_score,
            "violation_score": self.violation_score,
            "risk_multiplier": str(self.risk_multiplier),
            "last_updated": self.last_updated.isoformat(),
        }


# =============================================================================
# Default Tier Configurations
# =============================================================================

DEFAULT_TIER_PRICING: Dict[Tier, TierPricing] = {
    Tier.COMMUNITY: TierPricing(
        tier=Tier.COMMUNITY,
        base_price=Decimal("0"),
        included_units={
            UsageMetricType.API_CALLS: 10_000,
            UsageMetricType.ML_INFERENCES: 1_000,
            UsageMetricType.THREAT_DETECTIONS: 100,
            UsageMetricType.TELEMETRY_STORAGE_GB: 1,
        },
        overage_rates={
            UsageMetricType.API_CALLS: Decimal("0.001"),
            UsageMetricType.ML_INFERENCES: Decimal("0.01"),
        },
        hard_limits={
            UsageMetricType.API_CALLS: 50_000,
            UsageMetricType.ML_INFERENCES: 5_000,
            UsageMetricType.FEDERATED_ROUNDS: 0,
            UsageMetricType.CUSTOM_MODEL_DEPLOYMENTS: 0,
        },
        features={"basic_defense", "static_models"},
        ml_models_allowed={"anomaly_detection", "risk_scoring"},
    ),
    Tier.PROFESSIONAL: TierPricing(
        tier=Tier.PROFESSIONAL,
        base_price=Decimal("99"),
        included_units={
            UsageMetricType.API_CALLS: 100_000,
            UsageMetricType.ML_INFERENCES: 10_000,
            UsageMetricType.THREAT_DETECTIONS: 1_000,
            UsageMetricType.ENFORCEMENT_ACTIONS: 500,
            UsageMetricType.TELEMETRY_STORAGE_GB: 10,
            UsageMetricType.FEDERATED_ROUNDS: 4,
        },
        overage_rates={
            UsageMetricType.API_CALLS: Decimal("0.0008"),
            UsageMetricType.ML_INFERENCES: Decimal("0.008"),
            UsageMetricType.THREAT_DETECTIONS: Decimal("0.05"),
            UsageMetricType.FEDERATED_ROUNDS: Decimal("25"),
        },
        soft_limits={
            UsageMetricType.API_CALLS: 500_000,
            UsageMetricType.ML_INFERENCES: 50_000,
        },
        risk_pricing_enabled=True,
        max_risk_multiplier=Decimal("1.5"),
        features={
            "basic_defense", "static_models", "hybrid_models",
            "federated_learning", "drift_detection"
        },
        ml_models_allowed={
            "anomaly_detection", "risk_scoring", "pattern_learning", "predictive"
        },
    ),
    Tier.ENTERPRISE: TierPricing(
        tier=Tier.ENTERPRISE,
        base_price=Decimal("499"),
        included_units={
            UsageMetricType.API_CALLS: 1_000_000,
            UsageMetricType.ML_INFERENCES: 100_000,
            UsageMetricType.THREAT_DETECTIONS: 10_000,
            UsageMetricType.ENFORCEMENT_ACTIONS: 5_000,
            UsageMetricType.ANOMALY_ANALYSES: 10_000,
            UsageMetricType.TELEMETRY_STORAGE_GB: 100,
            UsageMetricType.MODEL_STORAGE_GB: 10,
            UsageMetricType.FEDERATED_ROUNDS: 52,
            UsageMetricType.CUSTOM_MODEL_DEPLOYMENTS: 5,
            UsageMetricType.CROWN_JEWEL_ACCESSES: 1_000,
        },
        overage_rates={
            UsageMetricType.API_CALLS: Decimal("0.0005"),
            UsageMetricType.ML_INFERENCES: Decimal("0.005"),
            UsageMetricType.THREAT_DETECTIONS: Decimal("0.03"),
            UsageMetricType.CUSTOM_MODEL_DEPLOYMENTS: Decimal("99"),
        },
        risk_pricing_enabled=True,
        max_risk_multiplier=Decimal("2.0"),
        features={"*"},  # All features
        ml_models_allowed={"*"},  # All models
    ),
}


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "UsageRecord",
    "TierPricing",
    "BillingPeriod",
    "UpsellTrigger",
    "UpsellEvent",
    "RiskPricingProfile",
    "DEFAULT_TIER_PRICING",
]
