from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CartItemInvoiceData:
    description: Optional[str] = None
