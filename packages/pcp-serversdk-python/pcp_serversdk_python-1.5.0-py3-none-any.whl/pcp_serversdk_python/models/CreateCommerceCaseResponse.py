from dataclasses import dataclass
from typing import Optional

from .CreateCheckoutResponse import CreateCheckoutResponse
from .CreationDateTime import CreationDateTime
from .Customer import Customer


@dataclass(kw_only=True)
class CreateCommerceCaseResponse:
    commerceCaseId: Optional[str] = None
    merchantReference: Optional[str] = None
    customer: Optional[Customer] = None
    checkout: Optional[CreateCheckoutResponse] = None
    creationDateTime: Optional[CreationDateTime] = None
