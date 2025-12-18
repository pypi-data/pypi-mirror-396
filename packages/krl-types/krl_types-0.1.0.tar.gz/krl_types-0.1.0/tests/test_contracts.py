# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
OpenAPI Contract Tests for krl-types ↔ krl-premium-backend compatibility.

These tests ensure that shared types remain compatible between the client SDK
and server API after consolidation.
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

import pytest

from krl_types.billing import (
    Tier,
    UsageMetricType,
    UsageRecord,
    TierPricing,
    BillingPeriod,
    Money,
    Currency,
)


class TestAPIContractCompatibility:
    """
    Contract tests to ensure krl-types structures match krl-premium-backend API expectations.
    
    These tests verify:
    1. Serialization format matches API schema
    2. Enum values match backend expectations
    3. Decimal precision is preserved
    """
    
    def test_tier_enum_matches_api(self):
        """Verify Tier enum values match backend API expectations."""
        expected_values = {
            "community",
            "professional",
            "team", 
            "enterprise",
            "custom",
        }
        actual_values = {t.value for t in Tier}
        assert actual_values == expected_values, (
            f"Tier enum mismatch: expected {expected_values}, got {actual_values}"
        )
    
    def test_usage_metric_type_matches_api(self):
        """Verify UsageMetricType enum values match backend API."""
        # These are the metric types the backend expects
        required_metrics = {
            "api_calls",
            "ml_inferences",
            "ml_training_minutes",
            "threat_detections",
            "compute_hours",
        }
        actual_values = {m.value for m in UsageMetricType}
        assert required_metrics.issubset(actual_values), (
            f"Missing required metrics: {required_metrics - actual_values}"
        )
    
    def test_usage_record_serialization_format(self):
        """Verify UsageRecord.to_dict() produces API-compatible JSON."""
        record = UsageRecord(
            record_id="rec_test_123",
            tenant_id="tenant_abc",
            metric_type=UsageMetricType.API_CALLS,
            quantity=Decimal("1234.5678"),
            timestamp=datetime(2025, 12, 13, 15, 30, 0),
            tier=Tier.PROFESSIONAL,
            unit_price=Decimal("0.001"),
            total_price=Decimal("1.23"),
            risk_multiplier=Decimal("1.15"),
        )
        
        serialized = record.to_dict()
        
        # Verify required fields
        assert "record_id" in serialized
        assert "tenant_id" in serialized
        assert "metric_type" in serialized
        assert "quantity" in serialized
        assert "timestamp" in serialized
        assert "tier" in serialized
        
        # Verify enum serialization (string values)
        assert serialized["metric_type"] == "api_calls"
        assert serialized["tier"] == "professional"
        
        # Verify timestamp format (ISO 8601)
        assert serialized["timestamp"] == "2025-12-13T15:30:00"
        
        # Verify Decimal serialization (string to preserve precision)
        assert serialized["quantity"] == "1234.5678"
        assert serialized["risk_multiplier"] == "1.15"
        
        # Verify JSON serializable
        json_str = json.dumps(serialized)
        assert isinstance(json_str, str)
    
    def test_usage_record_deserialization(self):
        """Verify UsageRecord.from_dict() can parse API responses."""
        api_response = {
            "record_id": "rec_from_api",
            "tenant_id": "tenant_xyz",
            "metric_type": "ml_inferences",
            "quantity": "5000",
            "timestamp": "2025-12-13T10:00:00",
            "tier": "enterprise",
            "unit_price": "0.01",
            "total_price": "50.00",
            "risk_multiplier": "1.0",
            "source": "api",
            "correlation_id": "corr_123",
            "risk_factors": {"dls_score": 0.95},
            "metadata": {"region": "us-east-1"},
        }
        
        record = UsageRecord.from_dict(api_response)
        
        assert record.record_id == "rec_from_api"
        assert record.metric_type == UsageMetricType.ML_INFERENCES
        assert record.quantity == Decimal("5000")
        assert record.tier == Tier.ENTERPRISE
        assert record.risk_factors == {"dls_score": 0.95}
    
    def test_money_stripe_compatibility(self):
        """Verify Money class produces Stripe-compatible values."""
        # Stripe expects amounts in cents (integer)
        price = Money("99.99", "USD")
        
        stripe_amount = price.to_stripe_cents()
        assert isinstance(stripe_amount, int)
        assert stripe_amount == 9999
        
        # Verify roundtrip
        recovered = Money.from_stripe_cents(stripe_amount, "USD")
        assert recovered.amount == price.amount
    
    def test_money_serialization_format(self):
        """Verify Money.to_dict() produces API-compatible JSON."""
        price = Money("149.99", Currency.USD)
        
        serialized = price.to_dict()
        
        # Verify structure
        assert "amount" in serialized
        assert "currency" in serialized
        assert "cents" in serialized
        
        # Verify types
        assert serialized["amount"] == "149.99"  # String for precision
        assert serialized["currency"] == "USD"   # ISO code
        assert serialized["cents"] == 14999      # Integer
        
        # Verify JSON serializable
        json_str = json.dumps(serialized)
        assert isinstance(json_str, str)
    
    def test_tier_pricing_serialization(self):
        """Verify TierPricing.to_dict() produces API-compatible format."""
        pricing = TierPricing(
            tier=Tier.PROFESSIONAL,
            base_price=Decimal("99"),
            included_units={
                UsageMetricType.API_CALLS: 100_000,
                UsageMetricType.ML_INFERENCES: 10_000,
            },
            overage_rates={
                UsageMetricType.API_CALLS: Decimal("0.0008"),
            },
            hard_limits={
                UsageMetricType.API_CALLS: 1_000_000,
            },
            features={"federated_learning", "drift_detection"},
        )
        
        serialized = pricing.to_dict()
        
        # Verify enum keys are serialized as strings
        assert "api_calls" in serialized["included_units"]
        assert serialized["included_units"]["api_calls"] == 100_000
        
        # Verify Decimal serialization
        assert serialized["base_price"] == "99"
        assert serialized["overage_rates"]["api_calls"] == "0.0008"
        
        # Verify sets become lists
        assert isinstance(serialized["features"], list)
        assert "federated_learning" in serialized["features"]
        
        # Verify JSON serializable
        json_str = json.dumps(serialized)
        assert isinstance(json_str, str)
    
    def test_billing_period_total_calculation(self):
        """Verify BillingPeriod.compute_total() matches backend logic."""
        period = BillingPeriod(
            period_id="bp_test",
            tenant_id="tenant_test",
            tier=Tier.PROFESSIONAL,
            start_date=datetime(2025, 12, 1),
            end_date=datetime(2025, 12, 31),
            base_charge=Decimal("99"),
            overage_charges={
                UsageMetricType.API_CALLS: Decimal("15.50"),
                UsageMetricType.ML_INFERENCES: Decimal("8.25"),
            },
            risk_adjustments=Decimal("5.00"),
            discounts=Decimal("10.00"),
        )
        
        total = period.compute_total()
        
        # Expected: 99 + 15.50 + 8.25 + 5.00 - 10.00 = 117.75
        expected = Decimal("117.75")
        assert total == expected
        assert period.total_charge == expected


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing code."""
    
    def test_deprecated_tier_aliases(self):
        """Verify deprecated tier aliases still work."""
        from krl_types.billing.enums import BillingTier, KRLTier, PricingTier
        
        # All aliases should point to Tier
        assert BillingTier.COMMUNITY == Tier.COMMUNITY
        assert KRLTier.ENTERPRISE == Tier.ENTERPRISE
        assert PricingTier.PROFESSIONAL == Tier.PROFESSIONAL
    
    def test_enum_string_comparison(self):
        """Verify enums can be compared with string values for migration."""
        tier = Tier.PROFESSIONAL
        
        # Common pattern in existing code
        assert tier.value == "professional"
        assert Tier("professional") == tier
