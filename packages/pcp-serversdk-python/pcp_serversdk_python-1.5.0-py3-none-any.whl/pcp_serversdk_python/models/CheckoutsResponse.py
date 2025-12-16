from dataclasses import dataclass

from .CheckoutResponse import CheckoutResponse


@dataclass(kw_only=True)
class CheckoutsResponse:
    numberOfCheckouts: int
    checkouts: list[CheckoutResponse]
