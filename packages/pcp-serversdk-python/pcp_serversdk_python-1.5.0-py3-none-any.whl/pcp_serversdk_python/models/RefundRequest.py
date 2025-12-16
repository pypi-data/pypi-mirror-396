from dataclasses import dataclass, field
from typing import Optional

from .PaymentReferences import PaymentReferences
from .PositiveAmountOfMoney import PositiveAmountOfMoney
from .ReturnInformation import ReturnInformation


@dataclass(kw_only=True)
class RefundRequest:
    amountOfMoney: Optional[PositiveAmountOfMoney] = None
    references: Optional[PaymentReferences] = None
    # "return" is a reserved keyword in Python, so we need to use a different name for the field:
    return_info: Optional[ReturnInformation] = field(
        default=None, metadata={"name": "return"}
    )

    # To adhere to the PAYONE API Schema, we need to use the name "return" externally.
    # However, to avoid conflicts with Python's reserved keyword "return",
    # we use "return_info" internally while mapping it to "return" for external interactions:
    def __post_init__(self):
        if self.return_info is not None:
            setattr(self, "return", self.return_info)

    def to_dict(self):
        result = {
            "amountOfMoney": self.amountOfMoney,
            "references": self.references,
            "return": self.return_info,
        }
        return result
