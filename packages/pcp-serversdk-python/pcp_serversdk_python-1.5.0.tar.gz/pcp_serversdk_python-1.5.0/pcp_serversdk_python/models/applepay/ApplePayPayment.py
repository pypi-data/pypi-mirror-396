from dataclasses import dataclass
from typing import Optional

from .ApplePayPaymentContact import ApplePayPaymentContact
from .ApplePayPaymentToken import ApplePayPaymentToken


@dataclass(kw_only=True)
class ApplePayPayment:
    token: Optional[ApplePayPaymentToken] = None
    billingContact: Optional[ApplePayPaymentContact] = None
    shippingContact: Optional[ApplePayPaymentContact] = None
