from dataclasses import dataclass
from typing import Optional

from .AuthorizationMode import AuthorizationMode
from .CardInfo import CardInfo
from .CardOnFileRecurringFrequency import CardOnFileRecurringFrequency
from .CardRecurrenceDetails import CardRecurrenceDetails
from .TransactionChannel import TransactionChannel
from .UnscheduledCardOnFileRequestor import UnscheduledCardOnFileRequestor
from .UnscheduledCardOnFileSequenceIndicator import (
    UnscheduledCardOnFileSequenceIndicator,
)


@dataclass(kw_only=True)
class CardPaymentMethodSpecificInput:
    authorizationMode: Optional[AuthorizationMode] = None
    recurring: Optional[CardRecurrenceDetails] = None
    paymentProcessingToken: Optional[str] = None
    reportingToken: Optional[str] = None
    transactionChannel: Optional[TransactionChannel] = None
    unscheduledCardOnFileRequestor: Optional[UnscheduledCardOnFileRequestor] = None
    unscheduledCardOnFileSequenceIndicator: Optional[
        UnscheduledCardOnFileSequenceIndicator
    ] = None
    paymentProductId: Optional[int] = None
    card: Optional[CardInfo] = None
    returnUrl: Optional[str] = None
    cardOnFileRecurringFrequency: Optional[CardOnFileRecurringFrequency] = None
    cardOnFileRecurringExpiration: Optional[str] = None
