from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class ContactDetails:
    emailAddress: Optional[str] = None
    phoneNumber: Optional[str] = None
