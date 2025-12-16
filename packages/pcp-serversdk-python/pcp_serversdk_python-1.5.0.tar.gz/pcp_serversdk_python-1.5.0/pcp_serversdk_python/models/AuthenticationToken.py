from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class AuthenticationToken:
    token: Optional[str] = None
    id: Optional[str] = None
    creationDate: Optional[str] = None
    expirationDate: Optional[str] = None
