from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CustomerDevice:
    acceptHeader: Optional[str] = None
    ipAddress: Optional[str] = None
    deviceToken: Optional[str] = None
    userAgent: Optional[str] = None
