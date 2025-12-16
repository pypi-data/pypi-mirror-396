from dataclasses import dataclass
from typing import Optional

from .PayoutOutput import PayoutOutput
from .StatusCategoryValue import StatusCategoryValue
from .StatusValue import StatusValue


@dataclass(kw_only=True)
class PayoutResponse:
    """Object that holds the payment-related properties for the refund of a Payment Information."""

    payoutOutput: Optional[PayoutOutput] = None
    """Payout output details."""

    status: Optional[StatusValue] = None
    """Status of the payout."""

    statusCategory: Optional[StatusCategoryValue] = None
    """Category of the payout status."""

    id: Optional[str] = None
    """Unique payment transaction identifier of the payment gateway."""
