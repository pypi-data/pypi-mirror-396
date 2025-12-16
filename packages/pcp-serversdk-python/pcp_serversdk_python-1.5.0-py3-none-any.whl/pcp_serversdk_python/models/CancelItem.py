from dataclasses import dataclass


@dataclass(kw_only=True)
class CancelItem:
    id: str
    quantity: int
