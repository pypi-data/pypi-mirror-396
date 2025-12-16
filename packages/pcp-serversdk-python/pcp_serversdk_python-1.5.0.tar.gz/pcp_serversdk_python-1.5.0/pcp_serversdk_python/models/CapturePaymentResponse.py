from dataclasses import dataclass
from typing import Optional

from .CaptureOutput import CaptureOutput
from .PaymentStatusOutput import PaymentStatusOutput
from .StatusValue import StatusValue


@dataclass(kw_only=True)
class CapturePaymentResponse:
    captureOutput: Optional[CaptureOutput] = None
    status: Optional[StatusValue] = None
    statusOutput: Optional[PaymentStatusOutput] = None
    id: Optional[str] = None
