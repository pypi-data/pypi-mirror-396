from dataclasses import dataclass
from typing import Optional

from .AmountOfMoney import AmountOfMoney
from .CardPaymentMethodSpecificOutput import CardPaymentMethodSpecificOutput
from .FinancingPaymentMethodSpecificOutput import FinancingPaymentMethodSpecificOutput
from .MobilePaymentMethodSpecificOutput import MobilePaymentMethodSpecificOutput
from .PaymentReferences import PaymentReferences
from .RedirectPaymentMethodSpecificOutput import RedirectPaymentMethodSpecificOutput
from .SepaDirectDebitPaymentMethodSpecificOutput import (
    SepaDirectDebitPaymentMethodSpecificOutput,
)


@dataclass(kw_only=True)
class PaymentOutput:
    amountOfMoney: Optional[AmountOfMoney] = None
    merchantParameters: Optional[str] = None
    references: Optional[PaymentReferences] = None
    cardPaymentMethodSpecificOutput: Optional[CardPaymentMethodSpecificOutput] = None
    mobilePaymentMethodSpecificOutput: Optional[MobilePaymentMethodSpecificOutput] = (
        None
    )
    paymentMethod: Optional[str] = None
    redirectPaymentMethodSpecificOutput: Optional[
        RedirectPaymentMethodSpecificOutput
    ] = None
    sepaDirectDebitPaymentMethodSpecificOutput: Optional[
        SepaDirectDebitPaymentMethodSpecificOutput
    ] = None
    financingPaymentMethodSpecificOutput: Optional[
        FinancingPaymentMethodSpecificOutput
    ] = None
