from dataclasses import dataclass


@dataclass(kw_only=True)
class ReturnItem:
    id: str
    quantity: int
