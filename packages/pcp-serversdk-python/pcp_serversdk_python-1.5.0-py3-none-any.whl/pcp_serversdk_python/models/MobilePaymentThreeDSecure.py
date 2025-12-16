from dataclasses import dataclass
from typing import Optional

from .RedirectionData import RedirectionData


@dataclass(kw_only=True)
class MobilePaymentThreeDSecure:
    """Object containing specific data regarding 3-D Secure for card digital wallets.

    Necessary to perform 3D Secure when there is no liability shift from the
    wallet and corresponding card network.
    """

    redirectionData: Optional[RedirectionData] = None
    """Data required for redirection during 3-D Secure authentication."""
