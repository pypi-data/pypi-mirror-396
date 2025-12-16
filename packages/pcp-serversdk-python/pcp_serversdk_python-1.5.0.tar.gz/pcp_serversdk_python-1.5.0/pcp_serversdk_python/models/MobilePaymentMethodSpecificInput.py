from dataclasses import dataclass
from typing import Optional

from .AuthorizationMode import AuthorizationMode
from .MobilePaymentThreeDSecure import MobilePaymentThreeDSecure
from .PaymentProduct302SpecificInput import PaymentProduct302SpecificInput


@dataclass(kw_only=True)
class MobilePaymentMethodSpecificInput:
    """Object containing the specific input details for mobile payments."""

    paymentProductId: Optional[int] = None
    """Payment product identifier - please check product documentation for possible values.
    @minimum 0
    @maximum 99999"""

    authorizationMode: Optional[AuthorizationMode] = None
    """Authorization mode for the mobile payment."""

    encryptedPaymentData: Optional[str] = None
    """The encrypted payment data, if decryption is required.
    Typically, you'd use encryptedCustomerInput in the root of the create payment request instead."""

    publicKeyHash: Optional[str] = None
    """Public Key Hash - A unique identifier to retrieve the key used by Apple to encrypt information."""

    ephemeralKey: Optional[str] = None
    """Ephemeral Key - A unique generated key used by Apple to encrypt data."""

    threeDSecure: Optional[MobilePaymentThreeDSecure] = None
    """Three-D Secure details for the mobile payment."""

    paymentProduct302SpecificInput: Optional[PaymentProduct302SpecificInput] = None
    """Specific input for payment product 302."""
