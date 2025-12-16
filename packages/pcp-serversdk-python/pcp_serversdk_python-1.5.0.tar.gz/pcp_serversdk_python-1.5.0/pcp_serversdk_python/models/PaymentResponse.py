from dataclasses import dataclass
from typing import Optional

from .PaymentOutput import PaymentOutput
from .PaymentStatusOutput import PaymentStatusOutput
from .StatusValue import StatusValue


@dataclass(kw_only=True)
class PaymentResponse:
    paymentOutput: Optional[PaymentOutput] = None
    status: Optional[StatusValue] = None
    statusOutput: Optional[PaymentStatusOutput] = None
    id: Optional[str] = None
