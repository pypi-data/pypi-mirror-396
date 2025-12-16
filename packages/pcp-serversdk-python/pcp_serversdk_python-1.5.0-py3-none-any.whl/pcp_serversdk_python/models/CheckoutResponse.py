from dataclasses import dataclass
from typing import Optional

from .AllowedPaymentActions import AllowedPaymentActions
from .AmountOfMoney import AmountOfMoney
from .CheckoutReferences import CheckoutReferences
from .CreationDateTime import CreationDateTime
from .PaymentExecution import PaymentExecution
from .PaymentInformationResponse import PaymentInformationResponse
from .Shipping import Shipping
from .ShoppingCartResult import ShoppingCartResult
from .StatusCheckout import StatusCheckout
from .StatusOutput import StatusOutput


@dataclass(kw_only=True)
class CheckoutResponse:
    commerceCaseId: Optional[str] = None
    checkoutId: Optional[str] = None
    merchantCustomerId: Optional[str] = None
    amountOfMoney: Optional[AmountOfMoney] = None
    references: Optional[CheckoutReferences] = None
    shipping: Optional[Shipping] = None
    shoppingCart: Optional[ShoppingCartResult] = None
    paymentExecutions: Optional[list[PaymentExecution]] = None
    checkoutStatus: Optional[StatusCheckout] = None
    statusOutput: Optional[StatusOutput] = None
    paymentInformation: Optional[list[PaymentInformationResponse]] = None
    creationDateTime: Optional[CreationDateTime] = None
    allowedPaymentActions: Optional[list[AllowedPaymentActions]] = None
