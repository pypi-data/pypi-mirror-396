from dataclasses import dataclass
from typing import Optional

from .CartItemPatch import CartItemPatch


@dataclass(kw_only=True)
class ShoppingCartPatch:
    items: Optional[list[CartItemPatch]] = None
