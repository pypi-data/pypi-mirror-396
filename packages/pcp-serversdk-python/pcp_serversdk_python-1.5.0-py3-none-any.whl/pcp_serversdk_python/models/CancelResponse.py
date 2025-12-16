from dataclasses import dataclass
from typing import Optional

from .CancelPaymentResponse import CancelPaymentResponse
from .ShoppingCartResult import ShoppingCartResult


@dataclass(kw_only=True)
class CancelResponse:
    cancelPaymentResponse: Optional[CancelPaymentResponse] = None
    shoppingCart: Optional[ShoppingCartResult] = None
