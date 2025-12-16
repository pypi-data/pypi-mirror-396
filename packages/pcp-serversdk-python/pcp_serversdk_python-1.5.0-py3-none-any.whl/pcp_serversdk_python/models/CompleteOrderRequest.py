from dataclasses import dataclass
from typing import Optional

from .CompletePaymentMethodSpecificInput import CompletePaymentMethodSpecificInput


@dataclass(kw_only=True)
class CompleteOrderRequest:
    """The Complete-Order request is the last step to finalize the initial Order.

    It requires the completePaymentMethodSpecificInput. The previously provided data
    from the Commerce Case, Checkout, and Order will automatically be loaded and used
    for the completion of the Order.
    """

    completePaymentMethodSpecificInput: Optional[CompletePaymentMethodSpecificInput] = (
        None
    )
    """Contains the specific input required to complete the payment."""
