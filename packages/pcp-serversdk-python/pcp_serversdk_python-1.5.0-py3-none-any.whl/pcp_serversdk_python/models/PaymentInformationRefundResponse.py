from dataclasses import dataclass
from typing import Optional

from .PayoutResponse import PayoutResponse


@dataclass(kw_only=True)
class PaymentInformationRefundResponse:
    """Response for a Payment Information refund request."""

    payment: Optional[PayoutResponse] = None
    """Details of the refund payment."""

    paymentExecutionId: Optional[str] = None
    """Reference to the payment execution."""
