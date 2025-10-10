from __future__ import annotations

from typing import Optional, Protocol, Sequence
from uuid import UUID

from backend.domain.value_objects.money import Money
from backend.domain.enums.order_status import OrderStatusEnum
from backend.domain.enums.cart_status import CartStatusEnum


class LineItemProtocol(Protocol):
    """
    Contract for order and cart items.
    """

    product_id: UUID
    quantity: int
    unit_price: Money

    @property
    def subtotal(self) -> Money:
        pass

    @property
    def currency(self) -> str:
        pass


class OrderLike(Protocol):
    items: Sequence[LineItemProtocol]
    total: Money
    status: OrderStatusEnum
    payment_intent_id: Optional[str]


class CartLike(Protocol):
    items: Sequence[LineItemProtocol]
    total: Money
    status: CartStatusEnum
    cart_currency: Optional[str]
