from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CardPaymentDetails:
    maskedCardNumber: Optional[str] = None
    paymentProcessingToken: Optional[str] = None
    reportingToken: Optional[str] = None
    cardAuthorizationId: Optional[str] = None
