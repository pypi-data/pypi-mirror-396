from dataclasses import dataclass


@dataclass(kw_only=True)
class OrderItem:
    id: str
    quantity: int
