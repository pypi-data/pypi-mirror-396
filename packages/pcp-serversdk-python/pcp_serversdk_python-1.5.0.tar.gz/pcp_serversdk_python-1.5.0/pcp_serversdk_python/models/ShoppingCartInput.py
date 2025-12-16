from dataclasses import dataclass
from typing import Optional

from .CartItemInput import CartItemInput


@dataclass(kw_only=True)
class ShoppingCartInput:
    items: Optional[list[CartItemInput]] = None
