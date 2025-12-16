from dataclasses import dataclass
from typing import Optional

from .AmountOfMoney import AmountOfMoney
from .CheckoutReferences import CheckoutReferences
from .PaymentMethodSpecificInput import PaymentMethodSpecificInput
from .References import References
from .Shipping import Shipping
from .ShoppingCartPatch import ShoppingCartPatch


@dataclass(kw_only=True)
class PatchCheckoutRequest:
    amountOfMoney: Optional[AmountOfMoney] = None
    references: Optional[CheckoutReferences] = None
    shipping: Optional[Shipping] = None
    shoppingCart: Optional[ShoppingCartPatch] = None
    paymentMethodSpecificInput: Optional[PaymentMethodSpecificInput] = None
    paymentReferences: Optional[References] = None
