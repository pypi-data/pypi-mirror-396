from dataclasses import dataclass
from typing import Optional

from .BankAccountInformation import BankAccountInformation


@dataclass(kw_only=True)
class PaymentProduct3392SpecificInput:
    bankAccountInformation: Optional[BankAccountInformation] = None
