from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from .ApplePaymentDataTokenInformation import ApplePaymentDataTokenInformation
from .Network import Network


class IntegrationType(Enum):
    """Type of Apple Pay integration."""

    MERCHANT_CERTIFICATE = (
        auto()
    )  # using your own certificate (paid Apple Pay account needed)
    MASS_ENABLEMENT = auto()  # using PAYONE certificate


@dataclass(kw_only=True)
class PaymentProduct302SpecificInput:
    """Object containing additional information needed for Apple Pay payment transactions."""

    integrationType: Optional[IntegrationType] = None
    """Type of your Apple Pay integration.
    - `MERCHANT_CERTIFICATE`: using your own certificate (paid Apple Pay account needed).
    - `MASS_ENABLEMENT`: using PAYONE certificate."""

    network: Optional[Network] = None
    """Network/Scheme of the card used for the payment.
    - `MASTERCARD`
    - `VISA`
    - `AMEX`
    - `GIROCARD`
    - `DISCOVER` (not supported yet)
    - `JCB` (not supported yet)"""

    token: Optional[ApplePaymentDataTokenInformation] = None
    """Token containing Apple Pay payment data."""

    domainName: Optional[str] = None
    """Domain of your Webshop. Needed for initializing the Apple Pay payment session
    when `integrationType` is `MASS_ENABLEMENT`."""

    displayName: Optional[str] = None
    """Name of your Store. Needed for initializing the Apple Pay payment session
    when `integrationType` is `MASS_ENABLEMENT`."""
