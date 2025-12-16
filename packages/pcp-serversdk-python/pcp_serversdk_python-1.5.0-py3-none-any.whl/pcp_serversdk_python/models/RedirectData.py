from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class RedirectData:
    redirectURL: Optional[str] = None
