from dataclasses import dataclass
from typing import Optional

from .AddressPersonal import AddressPersonal


@dataclass(kw_only=True)
class Shipping:
    address: Optional[AddressPersonal] = None
