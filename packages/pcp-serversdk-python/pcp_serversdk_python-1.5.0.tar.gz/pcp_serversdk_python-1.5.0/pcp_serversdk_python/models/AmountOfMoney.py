from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class AmountOfMoney:
    amount: Optional[int] = None
    currencyCode: str
