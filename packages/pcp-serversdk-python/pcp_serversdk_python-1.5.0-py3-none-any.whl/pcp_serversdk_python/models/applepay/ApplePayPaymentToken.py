from dataclasses import dataclass
from typing import Optional

from .ApplePayPaymentData import ApplePayPaymentData
from .ApplePayPaymentMethod import ApplePayPaymentMethod


@dataclass(kw_only=True)
class ApplePayPaymentToken:
    paymentData: Optional[ApplePayPaymentData] = None
    paymentMethod: Optional[ApplePayPaymentMethod] = None
    transactionIdentifier: Optional[str] = None
