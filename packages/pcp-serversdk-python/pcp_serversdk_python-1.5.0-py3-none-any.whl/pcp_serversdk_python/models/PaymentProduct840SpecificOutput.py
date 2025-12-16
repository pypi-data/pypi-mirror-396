from dataclasses import dataclass
from typing import Optional

from .Address import Address
from .PaymentProduct840CustomerAccount import PaymentProduct840CustomerAccount


@dataclass(kw_only=True)
class PaymentProduct840SpecificOutput:
    payPalTransactionId: Optional[str] = None
    billingAddress: Optional[Address] = None
    customerAccount: Optional[PaymentProduct840CustomerAccount] = None
    shippingAddress: Optional[Address] = None
