from dataclasses import dataclass

from .BankAccountInformation import BankAccountInformation


@dataclass(kw_only=True)
class PaymentProduct3391SpecificInput:
    installmentOptionId: str
    bankAccountInformation: BankAccountInformation
