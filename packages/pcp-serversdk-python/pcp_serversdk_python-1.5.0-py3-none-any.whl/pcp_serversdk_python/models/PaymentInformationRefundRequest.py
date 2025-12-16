from dataclasses import dataclass
from typing import Optional

from .PaymentReferences import PaymentReferences
from .PositiveAmountOfMoney import PositiveAmountOfMoney


@dataclass(kw_only=True)
class PaymentInformationRefundRequest:
    """Request to initiate a refund for a Payment Information of Checkout.

    It is possible to initiate multiple partial refunds by providing an amount that is
    lower than the total captured amount of the Payment Information.
    """

    amountOfMoney: PositiveAmountOfMoney
    """The amount of money to be refunded."""

    references: Optional[PaymentReferences] = None
    """References associated with the refund request."""

    accountHolder: Optional[str] = None
    """Account holder of the bank account. 
    
    Does not necessarily have to be the customer (e.g., joint accounts).
    The name of the account holder is required for payment methods that use a credit transfer
    for the refund (e.g., girocard, SEPA Direct Debit)."""
