from dataclasses import dataclass
from typing import Optional

from .ApplePaymentDataTokenHeaderInformation import (
    ApplePaymentDataTokenHeaderInformation,
)
from .ApplePaymentTokenVersion import ApplePaymentTokenVersion


@dataclass(kw_only=True)
class ApplePaymentDataTokenInformation:
    version: Optional[ApplePaymentTokenVersion] = None
    signature: Optional[str] = None
    header: Optional[ApplePaymentDataTokenHeaderInformation] = None
