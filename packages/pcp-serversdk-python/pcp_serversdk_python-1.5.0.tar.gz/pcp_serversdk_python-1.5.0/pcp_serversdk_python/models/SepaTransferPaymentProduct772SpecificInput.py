from dataclasses import dataclass
from typing import Optional

from .BankAccountInformation import BankAccountInformation


@dataclass(kw_only=True)
class SepaTransferPaymentProduct772SpecificInput:
    """Object containing the specific input details for SEPA credit transfers
    excluding cross-border ones."""

    bankAccountInformation: Optional[BankAccountInformation] = None
    """Bank account information for the SEPA transfer."""
