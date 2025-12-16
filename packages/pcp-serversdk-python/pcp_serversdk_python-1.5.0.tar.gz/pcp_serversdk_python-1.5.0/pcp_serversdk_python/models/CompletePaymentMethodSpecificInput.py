from dataclasses import dataclass
from typing import Optional

from .CompletePaymentProduct840SpecificInput import (
    CompletePaymentProduct840SpecificInput,
)
from .PaymentProduct3391SpecificInput import PaymentProduct3391SpecificInput


@dataclass(kw_only=True)
class CompletePaymentMethodSpecificInput:
    paymentProduct3391SpecificInput: Optional[PaymentProduct3391SpecificInput] = None
    paymentProduct840SpecificInput: Optional[
        CompletePaymentProduct840SpecificInput
    ] = None
