from dataclasses import dataclass
from typing import Optional

from .PaymentInstructions import PaymentInstructions
from .PaymentProduct3391SpecificOutput import PaymentProduct3391SpecificOutput


@dataclass(kw_only=True)
class FinancingPaymentMethodSpecificOutput:
    """Object containing the specific output details for financing payment methods (Buy Now Pay Later)."""

    paymentProductId: Optional[int] = None
    """Payment product identifier - please check product documentation for a full overview of possible values.
    Currently supported payment methods:
    - `3390` - PAYONE Secured Invoice
    - `3391` - PAYONE Secured Installment
    - `3392` - PAYONE Secured Direct Debit
    @minimum 0
    @maximum 99999
    """

    paymentProduct3391SpecificOutput: Optional[PaymentProduct3391SpecificOutput] = None
    """Specific output details for payment product 3391 (PAYONE Secured Installment)."""

    paymentInstructions: Optional[PaymentInstructions] = None
    """Payment instructions associated with the financing payment method."""
