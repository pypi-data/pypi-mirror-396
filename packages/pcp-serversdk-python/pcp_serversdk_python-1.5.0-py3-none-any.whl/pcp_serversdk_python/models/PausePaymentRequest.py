from dataclasses import dataclass

from .RefreshType import RefreshType


@dataclass(kw_only=True)
class PausePaymentRequest:
    """Request to refresh the payment status of a specific payment."""

    refreshType: RefreshType
    """Type of refresh action to be performed."""
