from dataclasses import dataclass
from typing import Optional

from .CancellationReason import CancellationReason


@dataclass(kw_only=True)
class CancelPaymentRequest:
    cancellationReason: Optional[CancellationReason] = None
