from dataclasses import dataclass
from typing import Optional

from .CompleteFinancingPaymentMethodSpecificInput import (
    CompleteFinancingPaymentMethodSpecificInput,
)
from .CompleteRedirectPaymentMethodSpecificInput import (
    CompleteRedirectPaymentMethodSpecificInput,
)
from .CustomerDevice import CustomerDevice
from .Order import Order


@dataclass(kw_only=True)
class CompletePaymentRequest:
    financingPaymentMethodSpecificInput: Optional[
        CompleteFinancingPaymentMethodSpecificInput
    ] = None
    redirectPaymentMethodSpecificInput: Optional[
        CompleteRedirectPaymentMethodSpecificInput
    ] = None
    order: Optional[Order] = None
    device: Optional[CustomerDevice] = None
