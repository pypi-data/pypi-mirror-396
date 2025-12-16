from dataclasses import dataclass
from typing import Optional

from .CancellationReason import CancellationReason
from .DeliveryInformation import DeliveryInformation
from .PaymentReferences import PaymentReferences


@dataclass(kw_only=True)
class CapturePaymentRequest:
    amount: Optional[int] = None
    isFinal: bool = False
    cancellationReason: Optional[CancellationReason] = None
    references: Optional[PaymentReferences] = None
    delivery: Optional[DeliveryInformation] = None
