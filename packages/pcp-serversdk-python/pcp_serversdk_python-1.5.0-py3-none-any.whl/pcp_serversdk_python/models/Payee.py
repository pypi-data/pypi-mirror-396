from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class Payee:
    """Payee bank account details as part of the payment instructions.

    Contains information about the bank account of the payee or beneficiary.
    """

    iban: str
    """IBAN of the payee's or beneficiary's bank account.
    The IBAN is the International Bank Account Number. It is an internationally agreed format for
    the BBAN and includes the ISO country code and two check digits."""

    name: str
    """Name of the payee."""

    bic: Optional[str] = None
    """Bank Identification Code."""
