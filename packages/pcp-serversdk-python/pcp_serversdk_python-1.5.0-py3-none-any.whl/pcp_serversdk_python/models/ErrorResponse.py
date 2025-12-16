from dataclasses import dataclass
from typing import Optional

from .APIError import APIError


@dataclass(kw_only=True)
class ErrorResponse:
    errorId: Optional[str] = None
    errors: Optional[list[APIError]] = None
