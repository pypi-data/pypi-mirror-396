from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class ApplePayPaymentDataHeader:
    applicationData: Optional[str] = None
    ephemeralPublicKey: Optional[str] = None
    wrappedKey: Optional[str] = None
    publicKeyHash: Optional[str] = None
    transactionId: Optional[str] = None
