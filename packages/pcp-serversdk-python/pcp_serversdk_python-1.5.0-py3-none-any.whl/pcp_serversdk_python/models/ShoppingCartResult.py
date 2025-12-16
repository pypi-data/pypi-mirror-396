from dataclasses import dataclass
from typing import Optional

from .CartItemResult import CartItemResult


@dataclass(kw_only=True)
class ShoppingCartResult:
    items: Optional[list[CartItemResult]] = None
