from dataclasses import dataclass
from typing import Optional

from .CartItemInput import CartItemInput


@dataclass(kw_only=True)
class DeliveryInformation:
    items: Optional[list[CartItemInput]] = None
