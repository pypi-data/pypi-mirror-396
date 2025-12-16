from dataclasses import dataclass
from typing import Optional

from .RefundPaymentResponse import RefundPaymentResponse
from .ShoppingCartResult import ShoppingCartResult


@dataclass(kw_only=True)
class ReturnResponse:
    returnPaymentResponse: Optional[RefundPaymentResponse] = None
    shoppingCart: Optional[ShoppingCartResult] = None
