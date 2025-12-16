from dataclasses import dataclass
from typing import Optional

from .InstallmentOption import InstallmentOption


@dataclass(kw_only=True)
class PaymentProduct3391SpecificOutput:
    installmentOptions: Optional[list[InstallmentOption]] = None
