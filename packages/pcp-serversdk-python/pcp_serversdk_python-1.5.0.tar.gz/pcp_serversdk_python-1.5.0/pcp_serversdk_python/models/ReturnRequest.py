from dataclasses import dataclass
from typing import Optional

from .ReturnItem import ReturnItem
from .ReturnType import ReturnType


@dataclass(kw_only=True)
class ReturnRequest:
    returnType: Optional[ReturnType] = None
    returnReason: Optional[str] = None
    returnItems: Optional[list[ReturnItem]] = None
