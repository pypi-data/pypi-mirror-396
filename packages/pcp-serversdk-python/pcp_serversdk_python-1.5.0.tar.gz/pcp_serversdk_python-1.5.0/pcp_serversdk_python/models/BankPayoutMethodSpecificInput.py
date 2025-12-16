from dataclasses import dataclass
from typing import Optional

from .SepaTransferPaymentProduct772SpecificInput import (
    SepaTransferPaymentProduct772SpecificInput,
)


@dataclass(kw_only=True)
class BankPayoutMethodSpecificInput:
    """Object containing the specific input details for SEPA transfers."""

    paymentProductId: Optional[int] = None
    """Payment product identifier - please check product documentation for a full 
    overview of possible values.
    
    Minimum: 0
    Maximum: 99999
    """

    paymentProduct772SpecificInput: Optional[
        SepaTransferPaymentProduct772SpecificInput
    ] = None
    """Specific input for SEPA transfer payment product 772."""
