# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Tests for krl-types billing module.
"""

from decimal import Decimal
from datetime import datetime
import pytest

from krl_types.billing import (
    # Enums
    Tier,
    CustomerSegment,
    ContractType,
    UsageMetricType,
    HealthCategory,
    ChurnRisk,
    # Currency
    Currency,
    Money,
    round_currency,
    to_cents,
    from_cents,
    usd,
    CurrencyMismatchError,
    # Models
    UsageRecord,
    TierPricing,
    BillingPeriod,
)


class TestTierEnum:
    """Tests for Tier enum."""
    
    def test_tier_values(self):
        assert Tier.COMMUNITY.value == "community"
        assert Tier.PROFESSIONAL.value == "professional"
        assert Tier.ENTERPRISE.value == "enterprise"
    
    def test_tier_display_name(self):
        assert Tier.COMMUNITY.display_name == "Community"
        assert Tier.PROFESSIONAL.display_name == "Professional"
    
    def test_tier_is_paid(self):
        assert not Tier.COMMUNITY.is_paid
        assert Tier.PROFESSIONAL.is_paid
        assert Tier.ENTERPRISE.is_paid


class TestContractType:
    """Tests for ContractType enum."""
    
    def test_contract_months(self):
        assert ContractType.MONTHLY.months == 1
        assert ContractType.ANNUAL.months == 12
        assert ContractType.MULTI_YEAR_2.months == 24
        assert ContractType.MULTI_YEAR_3.months == 36
    
    def test_contract_discounts(self):
        assert ContractType.MONTHLY.base_discount_bps == 0
        assert ContractType.ANNUAL.base_discount_bps == 1000  # 10%
        assert ContractType.MULTI_YEAR_3.base_discount_bps == 2000  # 20%


class TestHealthCategory:
    """Tests for HealthCategory enum."""
    
    def test_from_score(self):
        assert HealthCategory.from_score(10) == HealthCategory.CRITICAL
        assert HealthCategory.from_score(40) == HealthCategory.AT_RISK
        assert HealthCategory.from_score(60) == HealthCategory.HEALTHY
        assert HealthCategory.from_score(90) == HealthCategory.CHAMPION


class TestChurnRisk:
    """Tests for ChurnRisk enum."""
    
    def test_from_probability(self):
        assert ChurnRisk.from_probability(0.05) == ChurnRisk.LOW
        assert ChurnRisk.from_probability(0.20) == ChurnRisk.MEDIUM
        assert ChurnRisk.from_probability(0.45) == ChurnRisk.HIGH
        assert ChurnRisk.from_probability(0.75) == ChurnRisk.CRITICAL


class TestCurrency:
    """Tests for Currency enum."""
    
    def test_currency_properties(self):
        assert Currency.USD.code == "USD"
        assert Currency.USD.decimals == 2
        assert Currency.USD.symbol == "$"
        assert Currency.JPY.is_zero_decimal
        assert not Currency.USD.is_zero_decimal
    
    def test_smallest_unit(self):
        assert Currency.USD.smallest_unit == Decimal("0.01")
        assert Currency.JPY.smallest_unit == Decimal("1")
    
    def test_from_code(self):
        assert Currency.from_code("USD") == Currency.USD
        assert Currency.from_code("usd") == Currency.USD
        
        with pytest.raises(ValueError):
            Currency.from_code("XXX")


class TestRoundCurrency:
    """Tests for round_currency function."""
    
    def test_round_usd(self):
        assert round_currency(99.999, Currency.USD) == Decimal("100.00")
        assert round_currency(99.994, Currency.USD) == Decimal("99.99")
    
    def test_round_jpy(self):
        assert round_currency(99.5, Currency.JPY) == Decimal("100")
        assert round_currency(99.4, Currency.JPY) == Decimal("99")


class TestCentsConversion:
    """Tests for to_cents and from_cents functions."""
    
    def test_to_cents_usd(self):
        assert to_cents(Decimal("99.99"), Currency.USD) == 9999
        assert to_cents(100, Currency.USD) == 10000
    
    def test_to_cents_jpy(self):
        assert to_cents(Decimal("1000"), Currency.JPY) == 1000
    
    def test_from_cents_usd(self):
        assert from_cents(9999, Currency.USD) == Decimal("99.99")
    
    def test_from_cents_jpy(self):
        assert from_cents(1000, Currency.JPY) == Decimal("1000")
    
    def test_roundtrip(self):
        original = Decimal("123.45")
        cents = to_cents(original, Currency.USD)
        recovered = from_cents(cents, Currency.USD)
        assert original == recovered


class TestMoney:
    """Tests for Money class."""
    
    def test_creation(self):
        m = Money("99.99", "USD")
        assert m.amount == Decimal("99.99")
        assert m.currency == Currency.USD
    
    def test_convenience_constructor(self):
        m = usd(99.99)
        assert m.amount == Decimal("99.99")
        assert m.currency == Currency.USD
    
    def test_to_stripe_cents(self):
        m = Money("99.99", "USD")
        assert m.to_stripe_cents() == 9999
    
    def test_from_stripe_cents(self):
        m = Money.from_stripe_cents(9999, "USD")
        assert m.amount == Decimal("99.99")
    
    def test_addition(self):
        m1 = usd(50)
        m2 = usd(30)
        result = m1 + m2
        assert result.amount == Decimal("80.00")
    
    def test_subtraction(self):
        m1 = usd(100)
        m2 = usd(30)
        result = m1 - m2
        assert result.amount == Decimal("70.00")
    
    def test_multiplication(self):
        m = usd(10)
        result = m * 3
        assert result.amount == Decimal("30.00")
    
    def test_division(self):
        m = usd(100)
        result = m / 4
        assert result.amount == Decimal("25.00")
    
    def test_apply_discount(self):
        m = usd(100)
        discounted = m.apply_discount(Decimal("10"))  # 10% off
        assert discounted.amount == Decimal("90.00")
    
    def test_apply_tax(self):
        m = usd(100)
        with_tax = m.apply_tax(Decimal("8.5"))  # 8.5% tax
        assert with_tax.amount == Decimal("108.50")
    
    def test_currency_mismatch(self):
        m1 = Money(100, Currency.USD)
        m2 = Money(100, Currency.EUR)
        
        with pytest.raises(CurrencyMismatchError):
            _ = m1 + m2
    
    def test_comparison(self):
        m1 = usd(100)
        m2 = usd(50)
        m3 = usd(100)
        
        assert m1 > m2
        assert m2 < m1
        assert m1 == m3
        assert m1 >= m3
        assert m2 <= m1
    
    def test_to_dict(self):
        m = usd(99.99)
        d = m.to_dict()
        assert d["amount"] == "99.99"
        assert d["currency"] == "USD"
        assert d["cents"] == 9999
    
    def test_from_dict(self):
        d = {"amount": "99.99", "currency": "USD"}
        m = Money.from_dict(d)
        assert m.amount == Decimal("99.99")
        assert m.currency == Currency.USD


class TestUsageRecord:
    """Tests for UsageRecord model."""
    
    def test_creation(self):
        record = UsageRecord(
            record_id="rec_123",
            tenant_id="tenant_456",
            metric_type=UsageMetricType.API_CALLS,
            quantity=Decimal("1000"),
            timestamp=datetime(2025, 12, 13, 12, 0, 0),
            tier=Tier.PROFESSIONAL,
        )
        
        assert record.record_id == "rec_123"
        assert record.metric_type == UsageMetricType.API_CALLS
        assert record.quantity == Decimal("1000")
    
    def test_to_dict(self):
        record = UsageRecord(
            record_id="rec_123",
            tenant_id="tenant_456",
            metric_type=UsageMetricType.API_CALLS,
            quantity=Decimal("1000"),
            timestamp=datetime(2025, 12, 13, 12, 0, 0),
            tier=Tier.PROFESSIONAL,
        )
        
        d = record.to_dict()
        assert d["record_id"] == "rec_123"
        assert d["metric_type"] == "api_calls"
        assert d["tier"] == "professional"


class TestTierPricing:
    """Tests for TierPricing model."""
    
    def test_creation(self):
        pricing = TierPricing(
            tier=Tier.PROFESSIONAL,
            base_price=Decimal("99"),
            included_units={UsageMetricType.API_CALLS: 100_000},
            overage_rates={UsageMetricType.API_CALLS: Decimal("0.001")},
        )
        
        assert pricing.tier == Tier.PROFESSIONAL
        assert pricing.base_price == Decimal("99")
        assert pricing.included_units[UsageMetricType.API_CALLS] == 100_000


class TestBillingPeriod:
    """Tests for BillingPeriod model."""
    
    def test_compute_total(self):
        period = BillingPeriod(
            period_id="period_123",
            tenant_id="tenant_456",
            tier=Tier.PROFESSIONAL,
            start_date=datetime(2025, 12, 1),
            end_date=datetime(2025, 12, 31),
            base_charge=Decimal("99"),
            overage_charges={UsageMetricType.API_CALLS: Decimal("10")},
            risk_adjustments=Decimal("5"),
            discounts=Decimal("14"),
        )
        
        total = period.compute_total()
        # 99 + 10 + 5 - 14 = 100
        assert total == Decimal("100")
        assert period.total_charge == Decimal("100")
