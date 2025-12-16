from dataclasses import dataclass
from typing import Optional

from .CartItemOrderStatus import CartItemOrderStatus
from .OrderLineDetailsInput import OrderLineDetailsInput


@dataclass(kw_only=True)
class OrderLineDetailsPatch(OrderLineDetailsInput):
    id: Optional[str] = None
    status: Optional[list[CartItemOrderStatus]] = None
