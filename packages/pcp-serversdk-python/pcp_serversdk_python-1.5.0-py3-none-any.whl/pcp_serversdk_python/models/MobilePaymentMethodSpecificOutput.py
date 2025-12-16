from dataclasses import dataclass
from typing import Optional

from .CardFraudResults import CardFraudResults
from .ThreeDSecureResults import ThreeDSecureResults


@dataclass(kw_only=True)
class MobilePaymentMethodSpecificOutput:
    paymentProductId: Optional[int] = None
    authorisationCode: Optional[str] = None
    fraudResults: Optional[CardFraudResults] = None
    threeDSecureResults: Optional[ThreeDSecureResults] = None
    network: Optional[str] = None
