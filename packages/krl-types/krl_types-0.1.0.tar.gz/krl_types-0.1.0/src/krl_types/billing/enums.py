# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Centralized Billing Enums - Single Source of Truth.

All billing-related enums should be imported from this module
to avoid duplication and API/ABI drift across modules.

Usage:
    from krl_types.billing.enums import Tier, CustomerSegment, ContractType
"""

from enum import Enum, auto


# =============================================================================
# Core Tier & Segment Enums
# =============================================================================

class Tier(Enum):
    """
    KRL subscription tiers.
    
    Single source of truth for tier definitions.
    Maps to Stripe products and entitlements.
    """
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    PRO = "professional"  # Alias for PROFESSIONAL (backward compatibility)
    TEAM = "team"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"
    
    @property
    def display_name(self) -> str:
        return self.value.replace("_", " ").title()
    
    @property
    def is_paid(self) -> bool:
        return self != Tier.COMMUNITY


class CustomerSegment(Enum):
    """
    Customer segments for value-based pricing and targeting.
    
    Segments are based on:
    - Company size (employees, revenue)
    - Industry vertical
    - Usage patterns
    - Expansion potential
    """
    # Size-based segments
    STARTUP = "startup"           # <50 employees, seed/Series A
    SMB = "smb"                   # 50-200 employees
    MID_MARKET = "mid_market"     # 200-1000 employees
    ENTERPRISE = "enterprise"     # 1000-5000 employees
    STRATEGIC = "strategic"       # 5000+ employees, key accounts
    
    # Industry verticals
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    TECHNOLOGY = "technology"
    CONSULTING = "consulting"
    
    # Persona-based
    DEVELOPER = "developer"
    ANALYST = "analyst"
    DATA_SCIENTIST = "data_scientist"
    EXECUTIVE = "executive"
    
    @property
    def is_size_based(self) -> bool:
        return self in {
            CustomerSegment.STARTUP, CustomerSegment.SMB,
            CustomerSegment.MID_MARKET, CustomerSegment.ENTERPRISE,
            CustomerSegment.STRATEGIC
        }
    
    @property
    def is_industry_based(self) -> bool:
        return self in {
            CustomerSegment.FINANCE, CustomerSegment.HEALTHCARE,
            CustomerSegment.GOVERNMENT, CustomerSegment.ACADEMIC,
            CustomerSegment.TECHNOLOGY, CustomerSegment.CONSULTING
        }


# =============================================================================
# Contract Enums
# =============================================================================

class ContractType(Enum):
    """Contract commitment types with associated discount rates."""
    MONTHLY = "monthly"           # Month-to-month, no commitment
    ANNUAL = "annual"             # 12-month commitment
    MULTI_YEAR_2 = "multi_year_2" # 24-month commitment
    MULTI_YEAR_3 = "multi_year_3" # 36-month commitment
    ENTERPRISE = "enterprise"     # Custom enterprise terms
    
    @property
    def months(self) -> int:
        """Contract duration in months."""
        return {
            ContractType.MONTHLY: 1,
            ContractType.ANNUAL: 12,
            ContractType.MULTI_YEAR_2: 24,
            ContractType.MULTI_YEAR_3: 36,
            ContractType.ENTERPRISE: 36,  # Default for enterprise
        }.get(self, 12)
    
    @property
    def base_discount_bps(self) -> int:
        """Base commitment discount in basis points (100 bps = 1%)."""
        return {
            ContractType.MONTHLY: 0,
            ContractType.ANNUAL: 1000,        # 10%
            ContractType.MULTI_YEAR_2: 1500,  # 15%
            ContractType.MULTI_YEAR_3: 2000,  # 20%
            ContractType.ENTERPRISE: 2500,    # Up to 25%
        }.get(self, 0)


class ContractStatus(Enum):
    """Contract lifecycle states."""
    DRAFT = "draft"           # Being negotiated
    PENDING = "pending"       # Awaiting signature
    ACTIVE = "active"         # Currently in force
    EXPIRING = "expiring"     # Within 90 days of expiry
    EXPIRED = "expired"       # Past end date
    RENEWED = "renewed"       # Renewed to new contract
    CANCELLED = "cancelled"   # Terminated early
    SUSPENDED = "suspended"   # Temporarily suspended


class PaymentTerms(Enum):
    """Payment schedule options."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    PREPAID = "prepaid"
    
    @property
    def discount_bps(self) -> int:
        """Payment term discount in basis points."""
        return {
            PaymentTerms.MONTHLY: 0,
            PaymentTerms.QUARTERLY: 200,    # 2%
            PaymentTerms.SEMI_ANNUAL: 300,  # 3%
            PaymentTerms.ANNUAL: 500,       # 5%
            PaymentTerms.PREPAID: 800,      # 8%
        }.get(self, 0)


# =============================================================================
# Credit & Usage Enums
# =============================================================================

class CreditType(Enum):
    """Types of prepaid credits."""
    API_CALLS = "api_calls"
    ML_INFERENCE = "ml_inference"
    STORAGE_GB = "storage_gb"
    COMPUTE_HOURS = "compute_hours"
    SUPPORT_HOURS = "support_hours"
    GENERAL = "general_credits"


class UsageMetricType(Enum):
    """Billable usage metric types."""
    # API Usage
    API_CALLS = "api_calls"
    API_BANDWIDTH = "api_bandwidth"
    
    # ML Usage
    ML_INFERENCES = "ml_inferences"
    ML_TRAINING_MINUTES = "ml_training_minutes"
    FEDERATED_ROUNDS = "federated_rounds"
    
    # Defense Usage
    THREAT_DETECTIONS = "threat_detections"
    ENFORCEMENT_ACTIONS = "enforcement_actions"
    ANOMALY_ANALYSES = "anomaly_analyses"
    
    # Storage
    TELEMETRY_STORAGE_GB = "telemetry_storage_gb"
    MODEL_STORAGE_GB = "model_storage_gb"
    
    # Compute
    COMPUTE_HOURS = "compute_hours"
    
    # Premium Features
    CROWN_JEWEL_ACCESSES = "crown_jewel_accesses"
    CUSTOM_MODEL_DEPLOYMENTS = "custom_model_deployments"


# =============================================================================
# Health & Risk Enums
# =============================================================================

class HealthCategory(Enum):
    """Customer health score categories."""
    CRITICAL = "critical"   # 0-25: Immediate intervention needed
    AT_RISK = "at_risk"     # 26-50: Close monitoring required
    HEALTHY = "healthy"     # 51-75: Normal engagement
    CHAMPION = "champion"   # 76-100: Expansion candidates
    
    @classmethod
    def from_score(cls, score: float) -> "HealthCategory":
        """Determine category from score."""
        if score <= 25:
            return cls.CRITICAL
        elif score <= 50:
            return cls.AT_RISK
        elif score <= 75:
            return cls.HEALTHY
        else:
            return cls.CHAMPION


class ChurnRisk(Enum):
    """Churn risk levels."""
    LOW = "low"           # <10% probability
    MEDIUM = "medium"     # 10-30% probability
    HIGH = "high"         # 30-60% probability
    CRITICAL = "critical" # >60% probability
    
    @classmethod
    def from_probability(cls, prob: float) -> "ChurnRisk":
        """Determine risk level from probability."""
        if prob < 0.10:
            return cls.LOW
        elif prob < 0.30:
            return cls.MEDIUM
        elif prob < 0.60:
            return cls.HIGH
        else:
            return cls.CRITICAL


class InterventionType(Enum):
    """Types of proactive customer interventions."""
    CS_CALL = "customer_success_call"
    EXEC_OUTREACH = "executive_outreach"
    FEATURE_TRAINING = "feature_training"
    DISCOUNT_OFFER = "discount_offer"
    USAGE_REVIEW = "usage_review"
    INTEGRATION_HELP = "integration_help"
    UPGRADE_OFFER = "upgrade_offer"


# =============================================================================
# Pricing & Experiment Enums
# =============================================================================

class PricingStrategy(Enum):
    """Pricing strategies for different contexts."""
    FLAT_RATE = "flat_rate"
    USAGE_BASED = "usage_based"
    TIERED = "tiered"
    VALUE_BASED = "value_based"
    RISK_ADJUSTED = "risk_adjusted"
    DYNAMIC = "dynamic"


class ExperimentStatus(Enum):
    """Pricing experiment lifecycle states."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


class ExperimentType(Enum):
    """Types of pricing experiments."""
    PRICE_TEST = "price_test"
    DISCOUNT_TEST = "discount_test"
    TIER_TEST = "tier_test"
    FEATURE_TEST = "feature_test"


class ValueDriver(Enum):
    """
    Key value drivers that translate platform features into customer outcomes.
    Used to calculate ROI and justify value-based pricing.
    """
    TIME_SAVED = "time_saved"                     # Analyst hours saved per month
    COST_REDUCTION = "cost_reduction"             # Infrastructure/tool cost savings
    REVENUE_IMPACT = "revenue_impact"             # Revenue enabled by insights
    RISK_MITIGATION = "risk_mitigation"           # Compliance/audit cost avoidance
    DECISION_QUALITY = "decision_quality"         # Better decisions from data
    SPEED_TO_INSIGHT = "speed_to_insight"         # Faster time-to-value
    DATA_ACCESS = "data_access"                   # Unique data not available elsewhere
    MODEL_ACCURACY = "model_accuracy"             # Improved prediction quality


class RiskPricingFactor(Enum):
    """Factors that affect risk-adjusted pricing."""
    DLS_SCORE = "dls_score"
    THREAT_FREQUENCY = "threat_frequency"
    ANOMALY_RATE = "anomaly_rate"
    ENFORCEMENT_RATE = "enforcement_rate"
    DRIFT_SEVERITY = "drift_severity"
    VIOLATION_HISTORY = "violation_history"


class UpsellTriggerType(Enum):
    """Types of upsell triggers."""
    USAGE_THRESHOLD = "usage_threshold"
    FEATURE_GATE = "feature_gate"
    TIER_VIOLATION = "tier_violation"
    RISK_INCREASE = "risk_increase"
    VALUE_REALIZATION = "value_realization"
    BEHAVIORAL_PATTERN = "behavioral_pattern"


class RevenueEventType(Enum):
    """Types of revenue events."""
    USAGE_RECORDED = "usage_recorded"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    TIER_VIOLATION = "tier_violation"
    UPSELL_TRIGGERED = "upsell_triggered"
    INVOICE_GENERATED = "invoice_generated"
    PAYMENT_RECEIVED = "payment_received"
    CHURN_RISK = "churn_risk"
    EXPANSION_OPPORTUNITY = "expansion_opportunity"


# =============================================================================
# Audit & Compliance Enums
# =============================================================================

class AuditAction(Enum):
    """Actions tracked in audit log."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    ACTIVATE = "activate"
    SUSPEND = "suspend"
    RENEW = "renew"


class ActorType(Enum):
    """Types of actors performing actions."""
    USER = "user"
    SYSTEM = "system"
    API = "api"
    CRON = "cron"


# =============================================================================
# Stripe-Specific Enums
# =============================================================================

class StripeSyncStatus(Enum):
    """Stripe synchronization states."""
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"
    RETRY = "retry"


class StripeEntityType(Enum):
    """Stripe entity types we sync."""
    CUSTOMER = "customer"
    SUBSCRIPTION = "subscription"
    INVOICE = "invoice"
    PRICE = "price"
    PRODUCT = "product"
    PAYMENT_INTENT = "payment_intent"


# =============================================================================
# Deprecation Mappings (for backward compatibility)
# =============================================================================

# Alias for backward compatibility with existing code
BillingTier = Tier  # Deprecated: use Tier instead
KRLTier = Tier  # Deprecated: use Tier instead
PricingTier = Tier  # Deprecated: use Tier instead


# =============================================================================
# Exports
# =============================================================================

__all__ = [
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
]
