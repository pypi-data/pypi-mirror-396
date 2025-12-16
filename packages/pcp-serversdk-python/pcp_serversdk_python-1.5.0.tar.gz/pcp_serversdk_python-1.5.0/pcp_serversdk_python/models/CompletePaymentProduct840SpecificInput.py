from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CompletePaymentProduct840SpecificInput:
    """Payload for completing PayPal payments via JavaScript SDK"""

    javaScriptSdkFlow: bool = False
    action: Optional[str] = None
