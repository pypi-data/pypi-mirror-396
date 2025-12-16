from dataclasses import dataclass
from typing import Optional

from .BankAccountInformation import BankAccountInformation
from .MandateRecurrenceType import MandateRecurrenceType


@dataclass(kw_only=True)
class ProcessingMandateInformation:
    bankAccountIban: Optional[BankAccountInformation] = None
    recurrenceType: Optional[MandateRecurrenceType] = None
    uniqueMandateReference: Optional[str] = None
    dateOfSignature: Optional[str] = None
    creditorId: Optional[str] = None
