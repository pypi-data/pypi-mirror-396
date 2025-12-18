# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Currency-Safe Pricing Utilities for KRL Billing.

This module provides standardized currency handling to ensure:
- Consistent decimal precision across all billing operations
- Proper rounding using banker's rounding (ROUND_HALF_UP)
- Currency code validation (ISO 4217)
- Safe conversion between Decimal and external representations
- Audit-safe formatting for invoices and reports

Usage:
    from krl_types.billing.currency import Money, round_currency, to_cents, from_cents

    price = Money("99.99", "USD")
    discounted = price.apply_discount(Decimal("10"))  # 10% off
    stripe_amount = price.to_stripe_cents()  # 9999
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from enum import Enum
from typing import Any, Optional, Union
import re


class Currency(Enum):
    """
    Supported currencies (ISO 4217).
    
    Zero-decimal currencies (JPY, KRW, etc.) are handled specially
    in conversion methods.
    """
    USD = ("USD", 2, "$", "US Dollar")
    EUR = ("EUR", 2, "€", "Euro")
    GBP = ("GBP", 2, "£", "British Pound")
    JPY = ("JPY", 0, "¥", "Japanese Yen")  # Zero-decimal
    CAD = ("CAD", 2, "CA$", "Canadian Dollar")
    AUD = ("AUD", 2, "A$", "Australian Dollar")
    CHF = ("CHF", 2, "CHF", "Swiss Franc")
    CNY = ("CNY", 2, "¥", "Chinese Yuan")
    INR = ("INR", 2, "₹", "Indian Rupee")
    MXN = ("MXN", 2, "MX$", "Mexican Peso")
    BRL = ("BRL", 2, "R$", "Brazilian Real")
    KRW = ("KRW", 0, "₩", "South Korean Won")  # Zero-decimal
    
    def __init__(self, code: str, decimals: int, symbol: str, name: str):
        self.code = code
        self.decimals = decimals
        self.symbol = symbol
        self.display_name = name
    
    @property
    def is_zero_decimal(self) -> bool:
        """Check if currency uses zero decimal places (e.g., JPY, KRW)."""
        return self.decimals == 0
    
    @property
    def smallest_unit(self) -> Decimal:
        """Get smallest unit as Decimal (e.g., 0.01 for USD, 1 for JPY)."""
        if self.decimals == 0:
            return Decimal("1")
        return Decimal("0." + "0" * (self.decimals - 1) + "1")
    
    @classmethod
    def from_code(cls, code: str) -> "Currency":
        """Get Currency from ISO code string."""
        code_upper = code.upper()
        for currency in cls:
            if currency.code == code_upper:
                return currency
        raise ValueError(f"Unknown currency code: {code}")


# Precision constants
TWO_PLACES = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")
ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


class CurrencyError(Exception):
    """Base exception for currency operations."""
    pass


class InvalidAmountError(CurrencyError):
    """Raised when amount cannot be parsed or is invalid."""
    pass


class CurrencyMismatchError(CurrencyError):
    """Raised when operations are attempted with mismatched currencies."""
    pass


def round_currency(
    amount: Union[Decimal, float, str],
    currency: Currency = Currency.USD,
    rounding: str = ROUND_HALF_UP,
) -> Decimal:
    """
    Round amount to currency's standard precision.
    
    Args:
        amount: Amount to round
        currency: Currency for precision lookup
        rounding: Rounding mode (default: ROUND_HALF_UP)
        
    Returns:
        Properly rounded Decimal
        
    Example:
        >>> round_currency(99.999, Currency.USD)
        Decimal('100.00')
        >>> round_currency(99.999, Currency.JPY)
        Decimal('100')
    """
    try:
        dec_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError) as e:
        raise InvalidAmountError(f"Cannot convert '{amount}' to Decimal: {e}")
    
    return dec_amount.quantize(currency.smallest_unit, rounding=rounding)


def to_cents(
    amount: Union[Decimal, float, str],
    currency: Currency = Currency.USD,
) -> int:
    """
    Convert amount to smallest currency unit (cents/pence/etc).
    
    Used for Stripe API which expects amounts in cents.
    
    Args:
        amount: Amount in currency units (e.g., dollars)
        currency: Currency for conversion
        
    Returns:
        Integer amount in smallest unit
        
    Example:
        >>> to_cents(Decimal("99.99"), Currency.USD)
        9999
        >>> to_cents(Decimal("1000"), Currency.JPY)
        1000
    """
    rounded = round_currency(amount, currency)
    
    if currency.is_zero_decimal:
        return int(rounded)
    
    # Multiply by 10^decimals to get cents
    multiplier = Decimal(10 ** currency.decimals)
    return int(rounded * multiplier)


def from_cents(
    cents: int,
    currency: Currency = Currency.USD,
) -> Decimal:
    """
    Convert from smallest currency unit back to standard units.
    
    Args:
        cents: Amount in smallest unit
        currency: Currency for conversion
        
    Returns:
        Decimal in standard currency units
        
    Example:
        >>> from_cents(9999, Currency.USD)
        Decimal('99.99')
        >>> from_cents(1000, Currency.JPY)
        Decimal('1000')
    """
    if currency.is_zero_decimal:
        return Decimal(cents)
    
    divisor = Decimal(10 ** currency.decimals)
    return (Decimal(cents) / divisor).quantize(
        currency.smallest_unit, rounding=ROUND_HALF_UP
    )


def safe_decimal(
    value: Any,
    default: Optional[Decimal] = None,
) -> Decimal:
    """
    Safely convert value to Decimal.
    
    Args:
        value: Value to convert
        default: Default if conversion fails (raises if None)
        
    Returns:
        Decimal value
        
    Raises:
        InvalidAmountError: If conversion fails and no default
    """
    if value is None:
        if default is not None:
            return default
        raise InvalidAmountError("Cannot convert None to Decimal")
    
    if isinstance(value, Decimal):
        return value
    
    try:
        # Handle string with currency symbols
        if isinstance(value, str):
            # Remove common currency symbols and whitespace
            cleaned = re.sub(r'[\s$€£¥₹₩]', '', value)
            # Remove thousands separators (comma when not decimal separator)
            if ',' in cleaned and '.' in cleaned:
                # Assume , is thousands separator
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned and '.' not in cleaned:
                # Could be decimal separator (European format)
                # Check if it's likely a decimal (one comma, less than 3 digits after)
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    cleaned = cleaned.replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            return Decimal(cleaned)
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as e:
        if default is not None:
            return default
        raise InvalidAmountError(f"Cannot convert '{value}' to Decimal: {e}")


def apply_percentage(
    amount: Decimal,
    percentage: Decimal,
    currency: Currency = Currency.USD,
) -> Decimal:
    """
    Apply percentage to amount with proper rounding.
    
    Args:
        amount: Base amount
        percentage: Percentage as whole number (e.g., 10 for 10%)
        currency: Currency for precision
        
    Returns:
        Calculated amount rounded to currency precision
        
    Example:
        >>> apply_percentage(Decimal("100"), Decimal("10"), Currency.USD)
        Decimal('10.00')
    """
    result = amount * (percentage / HUNDRED)
    return round_currency(result, currency)


def apply_discount(
    amount: Decimal,
    discount_percent: Decimal,
    currency: Currency = Currency.USD,
) -> Decimal:
    """
    Apply discount percentage to amount.
    
    Args:
        amount: Original amount
        discount_percent: Discount as whole number (e.g., 15 for 15% off)
        currency: Currency for precision
        
    Returns:
        Discounted amount rounded to currency precision
        
    Example:
        >>> apply_discount(Decimal("100"), Decimal("15"), Currency.USD)
        Decimal('85.00')
    """
    discount_multiplier = (HUNDRED - discount_percent) / HUNDRED
    result = amount * discount_multiplier
    return round_currency(result, currency)


def format_currency(
    amount: Union[Decimal, float, str],
    currency: Currency = Currency.USD,
    include_code: bool = False,
) -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        currency: Currency for symbol and precision
        include_code: Whether to include ISO code (e.g., "USD")
        
    Returns:
        Formatted string (e.g., "$99.99" or "$99.99 USD")
        
    Example:
        >>> format_currency(Decimal("1234.56"), Currency.USD)
        '$1,234.56'
        >>> format_currency(Decimal("1234"), Currency.JPY, include_code=True)
        '¥1,234 JPY'
    """
    rounded = round_currency(amount, currency)
    
    # Format with thousands separator
    if currency.is_zero_decimal:
        formatted = f"{rounded:,.0f}"
    else:
        formatted = f"{rounded:,.{currency.decimals}f}"
    
    result = f"{currency.symbol}{formatted}"
    
    if include_code:
        result = f"{result} {currency.code}"
    
    return result


@dataclass
class Money:
    """
    Immutable money value with currency.
    
    Provides type-safe currency operations with automatic rounding.
    
    Example:
        price = Money("99.99", "USD")
        discounted = price.apply_discount(Decimal("10"))
        total = price + Money("50.00", "USD")
        stripe_cents = price.to_stripe_cents()
    """
    _amount: Decimal
    _currency: Currency
    
    def __init__(
        self,
        amount: Union[Decimal, float, str, int],
        currency: Union[Currency, str] = Currency.USD,
    ):
        """
        Initialize Money with automatic validation and rounding.
        
        Args:
            amount: Monetary amount
            currency: Currency code or Currency enum
        """
        # Convert currency
        if isinstance(currency, str):
            object.__setattr__(self, '_currency', Currency.from_code(currency))
        else:
            object.__setattr__(self, '_currency', currency)
        
        # Convert and round amount
        object.__setattr__(
            self, '_amount', 
            round_currency(safe_decimal(amount), self._currency)
        )
    
    @property
    def amount(self) -> Decimal:
        """Get the decimal amount."""
        return self._amount
    
    @property
    def currency(self) -> Currency:
        """Get the currency."""
        return self._currency
    
    def to_stripe_cents(self) -> int:
        """Convert to Stripe-compatible integer cents."""
        return to_cents(self._amount, self._currency)
    
    @classmethod
    def from_stripe_cents(
        cls, cents: int, currency: Union[Currency, str] = Currency.USD
    ) -> "Money":
        """Create Money from Stripe cents amount."""
        if isinstance(currency, str):
            currency = Currency.from_code(currency)
        return cls(from_cents(cents, currency), currency)
    
    def apply_discount(self, discount_percent: Decimal) -> "Money":
        """Return new Money with discount applied."""
        return Money(
            apply_discount(self._amount, discount_percent, self._currency),
            self._currency
        )
    
    def apply_tax(self, tax_percent: Decimal) -> "Money":
        """Return new Money with tax added."""
        tax_amount = apply_percentage(self._amount, tax_percent, self._currency)
        return Money(self._amount + tax_amount, self._currency)
    
    def multiply(self, factor: Union[Decimal, int, float]) -> "Money":
        """Return new Money multiplied by factor."""
        return Money(self._amount * Decimal(str(factor)), self._currency)
    
    def __add__(self, other: "Money") -> "Money":
        """Add two Money values."""
        self._check_currency_match(other)
        return Money(self._amount + other._amount, self._currency)
    
    def __sub__(self, other: "Money") -> "Money":
        """Subtract Money value."""
        self._check_currency_match(other)
        return Money(self._amount - other._amount, self._currency)
    
    def __mul__(self, factor: Union[Decimal, int, float]) -> "Money":
        """Multiply by scalar."""
        return self.multiply(factor)
    
    def __rmul__(self, factor: Union[Decimal, int, float]) -> "Money":
        """Reverse multiply by scalar."""
        return self.multiply(factor)
    
    def __truediv__(self, divisor: Union[Decimal, int, float]) -> "Money":
        """Divide by scalar."""
        if Decimal(str(divisor)) == ZERO:
            raise CurrencyError("Cannot divide by zero")
        return Money(self._amount / Decimal(str(divisor)), self._currency)
    
    def __neg__(self) -> "Money":
        """Negate the amount."""
        return Money(-self._amount, self._currency)
    
    def __abs__(self) -> "Money":
        """Absolute value."""
        return Money(abs(self._amount), self._currency)
    
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Money):
            return NotImplemented
        return self._amount == other._amount and self._currency == other._currency
    
    def __lt__(self, other: "Money") -> bool:
        """Less than comparison."""
        self._check_currency_match(other)
        return self._amount < other._amount
    
    def __le__(self, other: "Money") -> bool:
        """Less than or equal comparison."""
        self._check_currency_match(other)
        return self._amount <= other._amount
    
    def __gt__(self, other: "Money") -> bool:
        """Greater than comparison."""
        self._check_currency_match(other)
        return self._amount > other._amount
    
    def __ge__(self, other: "Money") -> bool:
        """Greater than or equal comparison."""
        self._check_currency_match(other)
        return self._amount >= other._amount
    
    def __hash__(self) -> int:
        """Hash for use in sets and dict keys."""
        return hash((self._amount, self._currency))
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"Money({self._amount!r}, {self._currency.code!r})"
    
    def __str__(self) -> str:
        """Human-readable string."""
        return format_currency(self._amount, self._currency)
    
    def _check_currency_match(self, other: "Money") -> None:
        """Ensure currencies match for operations."""
        if self._currency != other._currency:
            raise CurrencyMismatchError(
                f"Cannot operate on {self._currency.code} and {other._currency.code}"
            )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "amount": str(self._amount),
            "currency": self._currency.code,
            "cents": self.to_stripe_cents(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Money":
        """Create from dictionary."""
        return cls(data["amount"], data["currency"])
    
    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self._amount > ZERO
    
    def is_negative(self) -> bool:
        """Check if amount is negative."""
        return self._amount < ZERO
    
    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self._amount == ZERO


# Convenience functions for common operations
def usd(amount: Union[Decimal, float, str, int]) -> Money:
    """Create USD Money object."""
    return Money(amount, Currency.USD)


def eur(amount: Union[Decimal, float, str, int]) -> Money:
    """Create EUR Money object."""
    return Money(amount, Currency.EUR)


def gbp(amount: Union[Decimal, float, str, int]) -> Money:
    """Create GBP Money object."""
    return Money(amount, Currency.GBP)


# Invoice line item helper
@dataclass
class InvoiceLineItem:
    """
    Represents a line item on an invoice with currency-safe calculations.
    """
    description: str
    quantity: int
    unit_price: Money
    discount_percent: Decimal = ZERO
    tax_percent: Decimal = ZERO
    
    @property
    def subtotal(self) -> Money:
        """Calculate subtotal (quantity × unit price)."""
        return self.unit_price.multiply(self.quantity)
    
    @property
    def discount_amount(self) -> Money:
        """Calculate discount amount."""
        if self.discount_percent == ZERO:
            return Money(ZERO, self.unit_price.currency)
        return Money(
            apply_percentage(
                self.subtotal.amount, self.discount_percent, self.unit_price.currency
            ),
            self.unit_price.currency
        )
    
    @property
    def after_discount(self) -> Money:
        """Amount after discount."""
        return self.subtotal - self.discount_amount
    
    @property
    def tax_amount(self) -> Money:
        """Calculate tax amount (on discounted amount)."""
        if self.tax_percent == ZERO:
            return Money(ZERO, self.unit_price.currency)
        return Money(
            apply_percentage(
                self.after_discount.amount, self.tax_percent, self.unit_price.currency
            ),
            self.unit_price.currency
        )
    
    @property
    def total(self) -> Money:
        """Calculate total including tax."""
        return self.after_discount + self.tax_amount
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price.to_dict(),
            "subtotal": self.subtotal.to_dict(),
            "discount_percent": str(self.discount_percent),
            "discount_amount": self.discount_amount.to_dict(),
            "after_discount": self.after_discount.to_dict(),
            "tax_percent": str(self.tax_percent),
            "tax_amount": self.tax_amount.to_dict(),
            "total": self.total.to_dict(),
        }


# Module exports
__all__ = [
    # Core classes
    "Currency",
    "Money",
    "InvoiceLineItem",
    # Functions
    "round_currency",
    "to_cents",
    "from_cents",
    "safe_decimal",
    "apply_percentage",
    "apply_discount",
    "format_currency",
    # Convenience constructors
    "usd",
    "eur",
    "gbp",
    # Constants
    "TWO_PLACES",
    "FOUR_PLACES",
    "ZERO",
    "ONE",
    "HUNDRED",
    # Exceptions
    "CurrencyError",
    "InvalidAmountError",
    "CurrencyMismatchError",
]
