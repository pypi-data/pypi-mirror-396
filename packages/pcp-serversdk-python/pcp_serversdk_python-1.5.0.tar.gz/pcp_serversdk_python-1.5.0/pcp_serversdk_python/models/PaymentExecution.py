from dataclasses import dataclass
from typing import Optional

from .BankPayoutMethodSpecificInput import BankPayoutMethodSpecificInput
from .CardPaymentMethodSpecificInput import CardPaymentMethodSpecificInput
from .FinancingPaymentMethodSpecificInput import FinancingPaymentMethodSpecificInput
from .MobilePaymentMethodSpecificInput import MobilePaymentMethodSpecificInput
from .PaymentChannel import PaymentChannel
from .PaymentEvent import PaymentEvent
from .RedirectPaymentMethodSpecificInput import RedirectPaymentMethodSpecificInput
from .References import References
from .SepaDirectDebitPaymentMethodSpecificInput import (
    SepaDirectDebitPaymentMethodSpecificInput,
)


@dataclass(kw_only=True)
class PaymentExecution:
    """Object containing information of the payment with a specific payment method."""

    paymentExecutionId: Optional[str] = None
    """Unique ID of paymentExecution."""

    paymentId: Optional[str] = None
    """Unique payment transaction identifier of the payment gateway."""

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
    bankPayoutMethodSpecificInput: Optional[BankPayoutMethodSpecificInput] = None
    paymentChannel: Optional[PaymentChannel] = None
    references: Optional[References] = None
    previousPayment: Optional[str] = None
    """Previous payment ID, if applicable."""

    creationDateTime: Optional[str] = None
    """The date and time when the payment was created."""

    lastUpdated: Optional[str] = None
    """The date and time when the payment was last updated."""

    events: Optional[list[PaymentEvent]] = None
    """List of payment events associated with this payment execution."""
