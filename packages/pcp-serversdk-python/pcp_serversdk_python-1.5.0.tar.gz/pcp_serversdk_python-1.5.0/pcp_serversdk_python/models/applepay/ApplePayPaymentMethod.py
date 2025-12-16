from dataclasses import dataclass
from typing import Optional

from .ApplePayPaymentContact import ApplePayPaymentContact
from .ApplePayPaymentMethodType import ApplePayPaymentMethodType


@dataclass(kw_only=True)
class ApplePayPaymentMethod:
    displayName: Optional[str] = None
    network: Optional[str] = None
    type: Optional[ApplePayPaymentMethodType] = None
    paymentPass: Optional[str] = None
    billingContact: Optional[ApplePayPaymentContact] = None
