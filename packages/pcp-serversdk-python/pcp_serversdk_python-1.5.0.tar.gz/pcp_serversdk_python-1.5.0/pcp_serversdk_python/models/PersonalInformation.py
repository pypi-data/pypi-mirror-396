from dataclasses import dataclass
from typing import Optional

from .Gender import Gender
from .PersonalName import PersonalName


@dataclass(kw_only=True)
class PersonalInformation:
    dateOfBirth: Optional[str] = None
    gender: Optional[Gender] = None
    name: Optional[PersonalName] = None
