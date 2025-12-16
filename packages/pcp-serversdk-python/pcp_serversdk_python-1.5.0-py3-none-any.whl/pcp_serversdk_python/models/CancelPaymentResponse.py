from dataclasses import dataclass
from typing import Optional

from .PaymentResponse import PaymentResponse


@dataclass(kw_only=True)
class CancelPaymentResponse:
    payment: Optional[PaymentResponse] = None
