from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import partial
from uuid import UUID

from backend.domain.entities.cart_item import CartItem
from backend.domain.enums.cart_status import CartStatusEnum
from backend.domain.exceptions.base import (
    IllegalState,
    InvariantViolation
)
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
    - For an empty cart: cart_currency is None and
      total == 0 in DEFAULT_CURRENCY

    Policies:
    - total is always recalculated from items
    - cart_currency is fixed by the first item
      and must match all subsequent items
    - One cart currency per cart; mixed currencies are forbidden
    """

    user_id: UUID
    status: CartStatusEnum = CartStatusEnum.ACTIVE
    items: list[CartItem] = field(
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


    def add_item(self, item: LineItemProtocol) -> None:
        self._ensure_active()
        cart_item = (
            item if isinstance(item, CartItem)
            else CartItem.from_protocol(item)
        )
        if cart_item.quantity <= 0:
            raise InvariantViolation(
                'Quantity of the item must be > 0'
            )
        if self.items:
            if self.cart_currency != cart_item.currency:
                raise InvariantViolation(
                    'Item currency does not match cart currency'
                )
            item_in_cart = self._find_item(
                product_id=cart_item.product_id,
                unit_price=cart_item.unit_price
            )
            if item_in_cart:
                item_in_cart.quantity += cart_item.quantity
            else:
                self.items.append(cart_item)
        else:
            self.items.append(cart_item)
        self._recalculate_total()
        self._validate_invariants()
        self.version += 1


    def clear(self) -> None:
        """
        Command. Clear all items from the cart.

        Required fields (must be loaded before invocation):
            - id
            - status
            - payment_intent_id
            - version

        Preconditions:
            - Cart must be ACTIVE (guarded by _ensure_active()).
            - No checkout in progress (payment_intent_id is None).

        Postconditions:
            - items becomes empty
            - cart_currency is None
            - total == Money.zero(DEFAULT_CURRENCY)
            - version is incremented by 1
            - all invariants hold (_validate_invariants())

        Raises:
            IllegalState: if the cart is not ACTIVE or checkout is in progress.
        """
        # TODO add verification of not empty cart before clearing
        # for now, self.items implied as empty list in self.items
        self._ensure_active()
        if self.payment_intent_id:
            raise IllegalState('Cannot clear cart during checkout')
        self.items.clear()
        self._recalculate_total()
        self._validate_invariants()
        self.version += 1


    def _ensure_active(self) -> None:
        if self.status != CartStatusEnum.ACTIVE:
            raise IllegalState(
                'Cart is not active and cannot be modified'
            )


    def _ensure_single_currency(self) -> str | None:
        """
        Internal. Validate that all items share the same currency.
        
        Returns:
            str | None: common currency for non-empty carts, or None for empty carts.
        Raises:
            InvariantViolation: if mixed currencies are detected.
        Notes:
            Called by _recalculate_total() and _validate_invariants(). No side effects.
        """
        if not self.items:
            return None
        first_currency = self.items[0].currency
        for item in self.items:
            if item.currency != first_currency:
                raise InvariantViolation(
                    'Cart contains mixed currencies'
                )
        return first_currency


    def _find_item(
        self,
        product_id: UUID,
        unit_price: Money | None = None,
    ) -> CartItem | None:
        """
        Find an item by product_id and optional unit_price in self.items.
        Through unit_price can be used to distinguish between
        different variants of the same product.
        """
        for item in self.items:
            if item.product_id != product_id:
                continue
            if unit_price is not None and item.unit_price != unit_price:
                continue
            return item
        return None



    def _recalculate_total(self) -> None:
        """
        Internal. Recompute cart totals and currency from items.

        Behavior:
            - Empty cart: cart_currency=None; total=Money.zero(DEFAULT_CURRENCY)
            - Non-empty: cart_currency = single items' currency; total = sum(subtotals)
        Notes:
            Must be called after any items mutation.
        """
        if not self.items:
            self.cart_currency = None
            # Unlike cart_currency, for empty carts the Money type for the
            # total attribute requires a currency value, so apply DEFAULT_CURRENCY
            self.total = Money.zero(DEFAULT_CURRENCY)
            return
        self.cart_currency = self._ensure_single_currency()
        amount = sum(item.subtotal.amount for item in self.items)
        self.total = Money(amount, self.cart_currency)


    def _validate_invariants(self) -> None:
        """
        Internal. Assert Cart invariants (version ≥ 0, nonnegative totals,
        empty/non-empty state, currency consistency, total equals sum of items).
        
        Raises:
            InvariantViolation: if any invariant is violated.
        Side effects:
            None (pure validation).
        """
        if self.version < 0:
            raise InvariantViolation('version < 0')

        if self.total.amount < 0:
            raise InvariantViolation('total.amount < 0')

        if not self.items:
            if self.cart_currency is not None:
                raise InvariantViolation(
                    'cart_currency must be None for empty cart'
                )
            if (
                self.total.currency != DEFAULT_CURRENCY
                or self.total.amount != 0
            ):
                raise InvariantViolation(
                    'empty cart must have zero total in default currency'
                )
        else:
            items_currency = self._ensure_single_currency()

            if self.cart_currency is None:
                raise InvariantViolation(
                    'cart_currency must be set when cart has items'
                )
            if self.cart_currency != items_currency:
                raise InvariantViolation(
                    'cart currency must equal items currency'
                )
            if self.total.currency != self.cart_currency:
                raise InvariantViolation(
                    'total currency must equal cart currency'
                )
            # In case of updating Cart bypassing _recalculate_total
            expected_amount = sum(item.subtotal.amount for item in self.items)
            if self.total.amount != expected_amount:
                raise InvariantViolation(
                    'total amount must equal sum of item subtotals'
                )
