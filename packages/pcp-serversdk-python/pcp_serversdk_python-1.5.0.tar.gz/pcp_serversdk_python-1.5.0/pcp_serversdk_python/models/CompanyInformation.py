from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CompanyInformation:
    name: Optional[str] = None
