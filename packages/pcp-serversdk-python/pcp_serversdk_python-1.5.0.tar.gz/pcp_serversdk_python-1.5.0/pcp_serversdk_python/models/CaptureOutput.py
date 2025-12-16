from dataclasses import dataclass
from typing import Optional

from .AmountOfMoney import AmountOfMoney
from .PaymentInstructions import PaymentInstructions
from .PaymentReferences import PaymentReferences


@dataclass(kw_only=True)
class CaptureOutput:
    """Object containing Capture details."""

    amountOfMoney: Optional[AmountOfMoney] = None
    """Amount of money related to the capture."""

    merchantParameters: Optional[str] = None
    """Additional parameters for the transaction in JSON format.
    This field must not contain any personal data."""

    references: Optional[PaymentReferences] = None
    """References associated with the capture."""

    paymentMethod: Optional[str] = None
    """Payment method identifier used by the payment engine."""

    paymentInstructions: Optional[PaymentInstructions] = None
    """Payment instructions associated with the capture."""
