from dataclasses import dataclass
from typing import Optional

from .CartItemInput import CartItemInput


@dataclass(kw_only=True)
class ReturnInformation:
    returnReason: Optional[str] = None
    items: Optional[list[CartItemInput]] = None
