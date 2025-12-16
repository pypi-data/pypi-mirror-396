from dataclasses import dataclass
from typing import Optional

from .AmountOfMoney import AmountOfMoney
from .PaymentReferences import PaymentReferences


@dataclass(kw_only=True)
class PayoutOutput:
    """Object containing details from the created payout."""

    amountOfMoney: Optional[AmountOfMoney] = None
    """Amount of money details."""

    references: Optional[PaymentReferences] = None
    """Payment references associated with the payout."""

    paymentMethod: Optional[str] = None
    """Payment method identifier based on the paymentProductId."""
