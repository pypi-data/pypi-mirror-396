from dataclasses import dataclass
from typing import Optional

from .AllowedPaymentActions import AllowedPaymentActions
from .AmountOfMoney import AmountOfMoney
from .CheckoutReferences import CheckoutReferences
from .CreatePaymentResponse import CreatePaymentResponse
from .CreationDateTime import CreationDateTime
from .ErrorResponse import ErrorResponse
from .PaymentExecution import PaymentExecution
from .Shipping import Shipping
from .ShoppingCartResult import ShoppingCartResult
from .StatusCheckout import StatusCheckout
from .StatusOutput import StatusOutput


@dataclass(kw_only=True)
class CreateCheckoutResponse:
    checkoutId: Optional[str] = None
    shoppingCart: Optional[ShoppingCartResult] = None
    paymentResponse: Optional[CreatePaymentResponse] = None
    errorResponse: Optional[ErrorResponse] = None
    amountOfMoney: Optional[AmountOfMoney] = None
    references: Optional[CheckoutReferences] = None
    shipping: Optional[Shipping] = None
    paymentExecution: Optional[PaymentExecution] = None
    checkoutStatus: Optional[StatusCheckout] = None
    statusOutput: Optional[StatusOutput] = None
    creationDateTime: Optional[CreationDateTime] = None
    allowedPaymentActions: Optional[list[AllowedPaymentActions]] = None
