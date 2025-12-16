from dataclasses import dataclass
from typing import Optional

from .AvsResult import AvsResult


@dataclass(kw_only=True)
class CardFraudResults:
    avsResult: Optional[AvsResult] = None
