from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class PaymentProduct771SpecificOutput:
    mandateReference: Optional[str] = None
