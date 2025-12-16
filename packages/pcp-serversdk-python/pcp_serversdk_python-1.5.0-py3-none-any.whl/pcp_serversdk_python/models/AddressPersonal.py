from dataclasses import dataclass
from typing import Optional

from .PersonalName import PersonalName


@dataclass(kw_only=True)
class AddressPersonal:
    additionalInfo: Optional[str] = None
    city: Optional[str] = None
    countryCode: Optional[str] = None
    houseNumber: Optional[str] = None
    state: Optional[str] = None
    street: Optional[str] = None
    zip: Optional[str] = None
    name: Optional[PersonalName] = None
