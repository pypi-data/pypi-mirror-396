from dataclasses import dataclass
from typing import Optional

from .PaymentStatus import PaymentStatus


@dataclass(kw_only=True)
class StatusOutput:
    paymentStatus: Optional[PaymentStatus] = None
    isModifiable: Optional[bool] = None
    openAmount: Optional[int] = None
    collectedAmount: Optional[int] = None
    cancelledAmount: Optional[int] = None
    refundedAmount: Optional[int] = None
    chargebackAmount: Optional[int] = None
