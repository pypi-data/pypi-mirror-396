from dataclasses import dataclass
from typing import Optional

from .ActionType import ActionType
from .RedirectData import RedirectData


@dataclass(kw_only=True)
class MerchantAction:
    """Object that contains the action, including the needed data, that you should perform next, like showing
    instructions, showing the transaction results or redirect to a third party to complete the payment"""

    actionType: Optional[ActionType] = (
        None  # Action merchants needs to take in the online payment process
    )
    redirectData: Optional[RedirectData] = (
        None  # Object containing all data needed to redirect the customer
    )
