from dataclasses import dataclass
from typing import Optional

from .AmountOfMoney import AmountOfMoney
from .PaymentChannel import PaymentChannel
from .PaymentType import PaymentType


@dataclass(kw_only=True)
class PaymentInformationRequest:
    amountOfMoney: AmountOfMoney
    type: PaymentType
    paymentChannel: PaymentChannel
    paymentProductId: int
    merchantReference: Optional[str] = None
