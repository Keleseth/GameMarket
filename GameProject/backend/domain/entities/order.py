from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import partial
from typing import List, Optional
from uuid import UUID

from backend.core.config import DEFAULT_CURRENCY
from backend.domain.enums.order_status import OrderStatusEnum
from backend.domain.exceptions.base import (
	InvariantViolation,
	IllegalState
)
from backend.domain.protocols.common import LineItemProtocol
from backend.domain.value_objects.money import Money


# TODO rebuild using Cart as a reference
@dataclass(slots=True)
class Order:
	"""
	Order - Aggregate Root.

    Invariants:
    - total.amount ≥ 0
    - All items must use the same currency
    - In PAID status, the order contents are immutable
    - A paid order must not be empty

    Policies:
    - In DRAFT, total is recalculated from items;
	  after payment, total is fixed
    - Idempotency: repeated payment with the same payment_intent_id
	  is allowed (no-op); with a different one, it is an error
	"""

	id: UUID
	user_id: UUID
	status: OrderStatusEnum = OrderStatusEnum.PENDING
	items: List[LineItemProtocol] = field(default_factory=list)
	total: Money = field(default_factory=lambda: Money(0, DEFAULT_CURRENCY))
	created_at: datetime = field(
		default_factory=partial(datetime.now, timezone.utc)
    )
	version: int = 0
	payment_intent_id: Optional[str] = None

	def __post_init__(self):
		self._recalculate_total()
		self._validate_invariants()


	def add_item(self, item: LineItemProtocol) -> None:
		self._ensure_mutable()
		self._ensure_currency_compatible(item)
		for it in self.items:
			if it.product_id == item.product_id and it.unit_price == item.unit_price:
				it.change_quantity(it.quantity + item.quantity)
				break
		else:
			self.items.append(item)

		self._recalculate_total()
		self._validate_invariants()

	def set_item_quantity(self, product_id: UUID, new_qty: int) -> None:
		self._ensure_mutable()

		for it in self.items:
			if it.product_id == product_id:
				it.change_quantity(new_qty)
				self._recalculate_total()
				self._validate_invariants()
				return
		raise IllegalState('Item not found')

	def remove_item(self, product_id: UUID) -> None:
		self._ensure_mutable()
		before = len(self.items)
		self.items = [it for it in self.items if it.product_id != product_id]
		if len(self.items) == before:
			raise IllegalState('Item not found')
		self._recalculate_total()
		self._validate_invariants()

	def mark_payment_pending(self, payment_intent_id: str) -> None:
		"""
		Fixate payment intent before confirmation.
		"""
		if self.status == OrderStatusEnum.PAID:
			if self.payment_intent_id == payment_intent_id:
				return
			raise IllegalState('Order already paid with different intent')

		if self.payment_intent_id is None:
			self.payment_intent_id = payment_intent_id
		elif self.payment_intent_id != payment_intent_id:
			raise IllegalState('Different payment intent already set')

	def mark_paid(self, payment_intent_id: str) -> None:
		"""
		Confirm payment.
		"""
		if not self.items:
			raise IllegalState('Cannot pay empty order')

		if self.status == OrderStatusEnum.PAID:
			if self.payment_intent_id == payment_intent_id:
				return
			raise IllegalState('Order already paid with different intent')

		if self.payment_intent_id is None:
			self.payment_intent_id = payment_intent_id
		elif self.payment_intent_id != payment_intent_id:
			raise IllegalState('Different payment intent already set')

		self.status = OrderStatusEnum.PAID
		self._validate_invariants()

	def ensure_can_checkout(self) -> None:
		"""
		Invariants for starting payment.
		"""
		if self.status != OrderStatusEnum.DRAFT:
			raise IllegalState('Order is not in draft state')
		if not self.items:
			raise IllegalState('Order is empty')

	def _recalculate_total(self) -> None:
		if not self.items:
			self.total = Money(0, self.total.currency if hasattr(self.total, 'currency') else 'USD')
			return

		currency = self.items[0].currency
		amount = 0
		for item in self.items:
			if item.currency != currency:
				raise InvariantViolation('Mixed currencies in order')
			amount += item.subtotal.amount
		self.total = Money(amount, currency)

	def _validate_invariants(self) -> None:
		if self.total.amount < 0:
			raise InvariantViolation('Negative total')
		if self.status == OrderStatusEnum.PAID and not self.items:
			raise InvariantViolation('Paid order must have items')

	def _ensure_mutable(self) -> None:
		if self.status == OrderStatusEnum.PAID:
			raise IllegalState('Cannot modify a paid order')

	def _ensure_currency_compatible(self, item: LineItemProtocol) -> None:
		if not self.items:
			return
		current_currency = self.items[0].currency
		if item.currency != current_currency:
			raise InvariantViolation('Mixed currencies in order')
