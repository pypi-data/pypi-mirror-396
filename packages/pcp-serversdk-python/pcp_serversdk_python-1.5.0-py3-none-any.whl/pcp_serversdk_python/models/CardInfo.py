from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CardInfo:
    cardholderName: Optional[str] = None
