from dataclasses import dataclass, field
from functools import partial
from datetime import datetime, timezone
from uuid import UUID

from backend.domain.enums.cart_status import CartStatusEnum
from backend.domain.exceptions.base import InvariantViolation
from backend.domain.protocols.common import LineItemProtocol
from backend.domain.value_objects.money import Money
from backend.core.config import DEFAULT_CURRENCY



@dataclass(slots=True)
class Cart:
    """
    Cart - Aggregate Root for building a purchase before checkout.

    Invariants:
    - total.amount ≥ 0
    - All items must use the same currency
    - For an empty cart: cart_currency is None and total == 0 in DEFAULT_CURRENCY

    Policies:
    - total is always recalculated from items
    - cart_currency is fixed by the first item and must match all subsequent items
    - One cart currency per cart; mixed currencies are forbidden
    """

    user_id: UUID
    status: CartStatusEnum = CartStatusEnum.ACTIVE
    items: list[LineItemProtocol] = field(
        default_factory=list
    )
    total: Money = field(init=False)
    cart_currency: str | None = None
    created_at: datetime = field(
        default_factory=partial(datetime.now, timezone.utc)
    )
    version: int = 0
    payment_intent_id: str | None = None

    def __post_init__(self):
        self._recalculate_total()
        self._validate_invariants()

    def _recalculate_total(self):
        if not self.items:
            self.cart_currency = None
            # Unlike cart_currency For empty carts, Money type in total atr
            # require currency value, so applying DEFAULT_CURRENCY
            self.total = Money.zero(DEFAULT_CURRENCY)
            return
        amount = 0
        self.cart_currency = self._ensure_single_currency()
        amount = sum(item.subtotal.amount for item in self.items)
        self.total = Money(amount, self.cart_currency)

    def _validate_invariants(self):
        if self.version < 0:
            raise InvariantViolation('version < 0')

        if self.total.amount < 0:
            raise InvariantViolation('total.amount < 0')

        if not self.items:
            if self.cart_currency is not None:
                raise InvariantViolation(
                    'cart_currency must be None for empty cart'
                )
            # total currency for empty cart should be default
            if (
                self.total.currency != DEFAULT_CURRENCY
                or self.total.amount != 0
            ):
                raise InvariantViolation(
                    'empty cart must have zero total in default currency'
                )
        else:
            if self.cart_currency is None:
                raise InvariantViolation(
                    'cart_currency must be set when cart has items'
                )
            if self.total.currency != self.cart_currency:
                raise InvariantViolation(
                    'total currency must equal cart currency'
                )

    def _ensure_single_currency(self) -> str | None:
        if not self.items:
            return None
        first_currency = self.items[0].currency
        for item in self.items:
            if item.currency != first_currency:
                raise InvariantViolation('Cart contains mixed currencies')
        return first_currency