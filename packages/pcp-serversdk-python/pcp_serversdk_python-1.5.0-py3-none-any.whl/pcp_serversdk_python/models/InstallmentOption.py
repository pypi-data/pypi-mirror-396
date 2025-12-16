from dataclasses import dataclass

from .AmountOfMoney import AmountOfMoney
from .LinkInformation import LinkInformation


@dataclass(kw_only=True)
class InstallmentOption:
    installmentOptionId: str
    numberOfPayments: int
    monthlyAmount: AmountOfMoney
    lastRateAmount: AmountOfMoney
    effectiveInterestRate: int
    nominalInterestRate: int
    totalAmount: AmountOfMoney
    firstRateDate: str
    creditInformation: LinkInformation
