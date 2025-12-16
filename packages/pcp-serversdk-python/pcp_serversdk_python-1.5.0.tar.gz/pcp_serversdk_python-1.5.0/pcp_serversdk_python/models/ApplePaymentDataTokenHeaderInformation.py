from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class ApplePaymentDataTokenHeaderInformation:
    transactionId: Optional[str] = None
    applicationData: Optional[str] = None
