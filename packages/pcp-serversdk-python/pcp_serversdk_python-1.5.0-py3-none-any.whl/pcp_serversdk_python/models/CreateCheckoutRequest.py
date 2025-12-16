from dataclasses import dataclass
from typing import Optional

from .AmountOfMoney import AmountOfMoney
from .CheckoutReferences import CheckoutReferences
from .CreationDateTime import CreationDateTime
from .OrderRequest import OrderRequest
from .Shipping import Shipping
from .ShoppingCartInput import ShoppingCartInput


@dataclass(kw_only=True)
class CreateCheckoutRequest:
    amountOfMoney: Optional[AmountOfMoney] = None
    references: Optional[CheckoutReferences] = None
    shipping: Optional[Shipping] = None
    shoppingCart: Optional[ShoppingCartInput] = None
    orderRequest: Optional[OrderRequest] = None
    creationDateTime: Optional[CreationDateTime] = None
    autoExecuteOrder: Optional[bool] = False
