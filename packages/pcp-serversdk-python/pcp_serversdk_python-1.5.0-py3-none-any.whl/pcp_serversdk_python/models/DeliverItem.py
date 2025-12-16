from dataclasses import dataclass


@dataclass(kw_only=True)
class DeliverItem:
    id: str
    quantity: int
