from dataclasses import dataclass
from typing import Optional

from .PaymentStatusOutput import PaymentStatusOutput
from .RefundOutput import RefundOutput
from .StatusValue import StatusValue


@dataclass(kw_only=True)
class RefundPaymentResponse:
    refundOutput: Optional[RefundOutput] = None
    status: Optional[StatusValue] = None
    statusOutput: Optional[PaymentStatusOutput] = None
    id: Optional[str] = None
