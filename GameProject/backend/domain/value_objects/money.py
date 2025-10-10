# Money value object
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """
    Represents a monetary value with amount and currency.

    Attributes:
        amount (int): The amount in the smallest currency unit (e.g., cents).
        currency (str): The currency code (e.g., 'RUB', 'USD', 'EUR').
    """
    amount: int
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError('amount < 0')
        if not self.currency:
            raise ValueError('currency is empty')
        if (
            len(self.currency) != 3
            or not self.currency.isalpha()
            or not self.currency.isupper()
        ):
            raise ValueError('currency must be a 3-letter uppercase code')

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError('currency mismatch')
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: int) -> Money:
        if factor <= 0:
            raise ValueError('factor must be > 0')
        return Money(self.amount * factor, self.currency)

    def ensure_same_currency(self, other: Money):
        if self.currency != other.currency:
            raise ValueError('currency mismatch')

    @staticmethod
    def zero(currency: str) -> 'Money':
        """Convenience factory for a zero amount in a given currency."""
        return Money(0, currency)