from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CheckoutReferences:
    merchantReference: Optional[str] = None
    merchantShopReference: Optional[str] = None
