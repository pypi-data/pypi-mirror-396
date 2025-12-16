from dataclasses import dataclass
from typing import Optional

from .CompletePaymentProduct840SpecificInput import (
    CompletePaymentProduct840SpecificInput,
)


@dataclass(kw_only=True)
class CompleteRedirectPaymentMethodSpecificInput:
    paymentProductId: Optional[int] = None
    paymentProduct840SpecificInput: Optional[CompletePaymentProduct840SpecificInput] = (
        None
    )
