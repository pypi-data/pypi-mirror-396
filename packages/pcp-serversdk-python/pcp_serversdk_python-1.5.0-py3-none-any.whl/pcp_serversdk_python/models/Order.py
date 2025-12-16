from dataclasses import dataclass
from typing import Optional

from .AmountOfMoney import AmountOfMoney
from .Customer import Customer
from .References import References
from .Shipping import Shipping
from .ShoppingCartInput import ShoppingCartInput


@dataclass(kw_only=True)
class Order:
    amountOfMoney: Optional[AmountOfMoney] = None
    customer: Optional[Customer] = None
    references: Optional[References] = None
    shipping: Optional[Shipping] = None
    shoppingCart: Optional[ShoppingCartInput] = None
