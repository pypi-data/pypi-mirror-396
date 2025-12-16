from dataclasses import dataclass
from typing import Optional

from .CartItemStatus import CartItemStatus


@dataclass(kw_only=True)
class CartItemOrderStatus:
    cartItemStatus: Optional[CartItemStatus] = None
    quantity: Optional[int] = None
