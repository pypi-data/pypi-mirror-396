from dataclasses import dataclass
from typing import Optional

from .StatusCategoryValue import StatusCategoryValue


@dataclass(kw_only=True)
class PaymentStatusOutput:
    isCancellable: Optional[bool] = None
    statusCategory: Optional[StatusCategoryValue] = None
    isAuthorized: Optional[bool] = None
    isRefundable: Optional[bool] = None
