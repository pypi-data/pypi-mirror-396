from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class References:
    descriptor: Optional[str] = None
    merchantReference: str
    merchantParameters: Optional[str] = None
