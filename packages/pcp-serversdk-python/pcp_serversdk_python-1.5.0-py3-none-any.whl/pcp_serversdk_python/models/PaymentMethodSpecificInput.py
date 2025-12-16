from dataclasses import dataclass
from typing import Optional

from .CardPaymentMethodSpecificInput import CardPaymentMethodSpecificInput
from .CustomerDevice import CustomerDevice
from .FinancingPaymentMethodSpecificInput import FinancingPaymentMethodSpecificInput
from .MobilePaymentMethodSpecificInput import MobilePaymentMethodSpecificInput
from .PaymentChannel import PaymentChannel
from .RedirectPaymentMethodSpecificInput import RedirectPaymentMethodSpecificInput
from .SepaDirectDebitPaymentMethodSpecificInput import (
    SepaDirectDebitPaymentMethodSpecificInput,
)


@dataclass(kw_only=True)
class PaymentMethodSpecificInput:
    cardPaymentMethodSpecificInput: Optional[CardPaymentMethodSpecificInput] = None
    mobilePaymentMethodSpecificInput: Optional[MobilePaymentMethodSpecificInput] = None
    redirectPaymentMethodSpecificInput: Optional[RedirectPaymentMethodSpecificInput] = (
        None
    )
    sepaDirectDebitPaymentMethodSpecificInput: Optional[
        SepaDirectDebitPaymentMethodSpecificInput
    ] = None
    financingPaymentMethodSpecificInput: Optional[
        FinancingPaymentMethodSpecificInput
    ] = None
    customerDevice: Optional[CustomerDevice] = None
    paymentChannel: Optional[PaymentChannel] = None
