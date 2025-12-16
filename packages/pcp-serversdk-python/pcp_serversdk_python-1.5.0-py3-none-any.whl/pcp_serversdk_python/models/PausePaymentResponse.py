from dataclasses import dataclass
from typing import Optional

from .StatusValue import StatusValue


@dataclass(kw_only=True)
class PausePaymentResponse:
    """Response for pausing a payment."""

    status: Optional[StatusValue] = None
    """Status of the paused payment."""
