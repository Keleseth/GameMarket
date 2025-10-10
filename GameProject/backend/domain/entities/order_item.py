from dataclasses import dataclass
from uuid import UUID
from backend.domain.value_objects.money import Money


@dataclass(slots=True)
class OrderItem:

    product_id: UUID
    quantity: int
    unit_price: Money

    MAX_QTY: int = 100

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError('quantity must be > 0')
        if self.quantity > self.MAX_QTY:
            raise ValueError(f'quantity must be <= {self.MAX_QTY}')
        if not isinstance(self.unit_price, Money):
            raise TypeError('unit_price must be Money object')

    @property
    def subtotal(self) -> Money:
        return self.unit_price.multiply(self.quantity)

    @property
    def currency(self) -> str:
        """
        Access the currency of the OrderItem (Money.currency).
        """
        return self.unit_price.currency

    def change_quantity(self, new_qty: int) -> None:
        if new_qty <= 0:
            raise ValueError('quantity must be > 0')
        if new_qty > self.MAX_QTY:
            raise ValueError(f'quantity must be <= {self.MAX_QTY}')
        self.quantity = new_qty

    def with_quantity(self, new_qty: int) -> 'OrderItem':
        """
        Return a copy of the OrderItem with a new quantity.
        """
        if new_qty <= 0:
            raise ValueError('quantity must be > 0')
        if new_qty > self.MAX_QTY:
            raise ValueError(f'quantity must be <= {self.MAX_QTY}')
        return OrderItem(
            product_id=self.product_id,
            quantity=new_qty,
            unit_price=self.unit_price
        )
