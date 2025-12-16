from dataclasses import dataclass
from typing import Optional

from .RecurringPaymentSequenceIndicator import RecurringPaymentSequenceIndicator


@dataclass(kw_only=True)
class CardRecurrenceDetails:
    recurringPaymentSequenceIndicator: Optional[RecurringPaymentSequenceIndicator] = (
        None
    )
