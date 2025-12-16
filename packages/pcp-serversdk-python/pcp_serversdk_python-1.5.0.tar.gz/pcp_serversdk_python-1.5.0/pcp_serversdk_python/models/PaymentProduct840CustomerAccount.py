from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class PaymentProduct840CustomerAccount:
    companyName: Optional[str] = None
    firstName: Optional[str] = None
    payerId: Optional[str] = None
    surname: Optional[str] = None
