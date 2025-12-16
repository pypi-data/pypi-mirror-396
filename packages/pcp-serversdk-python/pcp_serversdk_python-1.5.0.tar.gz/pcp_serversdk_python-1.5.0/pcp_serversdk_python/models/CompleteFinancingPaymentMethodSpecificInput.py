from dataclasses import dataclass
from typing import Optional

from .PaymentProduct3391SpecificInput import PaymentProduct3391SpecificInput


@dataclass(kw_only=True)
class CompleteFinancingPaymentMethodSpecificInput:
    paymentProductId: Optional[int] = None
    requiresApproval: Optional[bool] = True
    paymentProduct3391SpecificInput: Optional[PaymentProduct3391SpecificInput] = None
