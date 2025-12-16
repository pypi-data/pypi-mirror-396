from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class PaymentCreationOutput:
    externalReference: Optional[str] = None
