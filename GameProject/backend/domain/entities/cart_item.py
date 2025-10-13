from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from backend.domain.value_objects.money import Money
from backend.domain.protocols.common import LineItemProtocol
from backend.domain.exceptions.base import InvariantViolation


@dataclass(slots=True)
class CartItem:
    """
    Mutable line item used inside Cart.

    Invariants:
    - quantity > 0
    - currency is derived from unit_price.currency
    - subtotal == quantity * unit_price
    """

    product_id: UUID
    quantity: int
    unit_price: Money

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvariantViolation('quantity must be > 0')

    @property
    def subtotal(self) -> Money:
        return self.unit_price.multiply(self.quantity)

    @property
    def currency(self) -> str:
        return self.unit_price.currency

    @classmethod
    def from_protocol(cls, item: LineItemProtocol) -> 'CartItem':
        if item.currency != item.unit_price.currency:
            raise InvariantViolation(
                'item.currency must equal unit_price.currency'
            )
        return cls(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
