from dataclasses import dataclass
from typing import Optional

from .Payee import Payee


@dataclass(kw_only=True)
class PaymentInstructions:
    """Object containing information on payment instructions details (e.g. on invoice payments)."""

    payee: Payee
    """Payee details."""

    dueDate: str
    """Due date of the payment in the format: YYYYMMDD."""

    referenceNumber: str
    """External payment reference number as part of payment instructions for the consumer."""

    status: Optional[str] = None
    """Status, usually describing the status of the invoice (e.g., paid, overdue, open)."""
