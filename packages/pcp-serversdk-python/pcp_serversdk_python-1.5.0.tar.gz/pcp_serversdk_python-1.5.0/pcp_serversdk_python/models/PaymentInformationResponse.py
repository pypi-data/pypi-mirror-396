from dataclasses import dataclass
from typing import Optional

from .CardPaymentDetails import CardPaymentDetails
from .PaymentChannel import PaymentChannel
from .PaymentEvent import PaymentEvent


@dataclass(kw_only=True)
class PaymentInformationResponse:
    """Object containing the related data of the created Payment Information."""

    commerceCaseId: Optional[str] = None
    """Unique ID of the Commerce Case."""

    checkoutId: Optional[str] = None
    """Unique ID of the Checkout."""

    merchantCustomerId: Optional[str] = None
    """Unique identifier of the customer."""

    paymentInformationId: Optional[str] = None
    """Unique ID of the Payment Information."""

    paymentChannel: Optional[PaymentChannel] = None
    """Payment channel used for this payment."""

    paymentProductId: Optional[int] = None
    """Payment product identifier - please check product documentation for possible values."""

    terminalId: Optional[str] = None
    """Unique identifier of the POS terminal of the payment transaction."""

    cardAcceptorId: Optional[str] = None
    """Unique ID identifying a store location or transaction point."""

    merchantReference: Optional[str] = None
    """Unique reference of the PaymentInformation."""

    creationDateTime: Optional[str] = None
    """The date and time when the payment was created."""

    lastUpdated: Optional[str] = None
    """The date and time when the payment was last updated."""

    cardPaymentDetails: Optional[CardPaymentDetails] = None
    """Card payment details related to the transaction."""

    events: Optional[list[PaymentEvent]] = None
    """List of payment events related to the transaction."""
