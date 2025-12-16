from dataclasses import dataclass
from typing import Optional

from .AppliedExemption import AppliedExemption


@dataclass(kw_only=True)
class ThreeDSecureResults:
    version: Optional[str] = None
    scheme_eci: Optional[str] = None
    applied_exemption: Optional[AppliedExemption] = None
