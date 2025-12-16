from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class PersonalName:
    firstName: Optional[str] = None
    surname: Optional[str] = None
    title: Optional[str] = None
