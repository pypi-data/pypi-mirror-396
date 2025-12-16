from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class PaymentReferences:
    merchantReference: Optional[str] = None
