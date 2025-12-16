from dataclasses import dataclass
from typing import Optional

from .ApplePayPaymentDataHeader import ApplePayPaymentDataHeader


@dataclass(kw_only=True)
class ApplePayPaymentData:
    data: Optional[str] = None
    header: Optional[ApplePayPaymentDataHeader] = None
    signature: Optional[str] = None
    version: Optional[str] = None
