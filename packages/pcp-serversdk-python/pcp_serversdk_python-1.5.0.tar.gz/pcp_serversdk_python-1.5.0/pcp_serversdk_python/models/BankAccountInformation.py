from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class BankAccountInformation:
    """Object containing information about the end customer's bank account."""

    iban: str
    """IBAN of the end customer's bank account. The IBAN is the International Bank
    Account Number. It is an internationally agreed format for the BBAN and
    includes the ISO country code and two check digits."""

    accountHolder: str
    """Account holder of the bank account with the given IBAN.
    Does not necessarily have to be the end customer (e.g., joint accounts)."""

    bic: Optional[str] = None
    """Bank Identification Code."""
