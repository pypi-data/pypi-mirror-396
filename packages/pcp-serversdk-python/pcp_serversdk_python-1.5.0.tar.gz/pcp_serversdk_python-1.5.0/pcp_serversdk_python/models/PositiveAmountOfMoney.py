from dataclasses import dataclass


@dataclass(kw_only=True)
class PositiveAmountOfMoney:
    amount: int
    currencyCode: str
