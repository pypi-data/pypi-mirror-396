from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CustomerAccount:
    """Object containing data related to the account the customer has with you."""

    createDate: Optional[str] = (
        None  # Creation date and time of the customer account in ISO 8601 format (UTC)
    )
