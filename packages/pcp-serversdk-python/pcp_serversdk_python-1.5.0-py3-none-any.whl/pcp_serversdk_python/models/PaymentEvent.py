from dataclasses import dataclass
from typing import Optional

from .AmountOfMoney import AmountOfMoney
from .CancellationReason import CancellationReason
from .PaymentInstructions import PaymentInstructions
from .PaymentType import PaymentType
from .StatusValue import StatusValue


@dataclass(kw_only=True)
class PaymentEvent:
    """Detailed information regarding an occurred payment event."""

    type: Optional[PaymentType] = None
    """Type of payment event."""

    amountOfMoney: Optional[AmountOfMoney] = None
    """Amount of money associated with the payment event."""

    paymentStatus: Optional[StatusValue] = None
    """Current status of the payment."""

    cancellationReason: Optional[CancellationReason] = None
    """Reason for payment cancellation."""

    returnReason: Optional[str] = None
    """Reason for refund (e.g., communicated by or to the customer)."""

    paymentInstructions: Optional[PaymentInstructions] = None
    """Payment instructions associated with this payment event."""
