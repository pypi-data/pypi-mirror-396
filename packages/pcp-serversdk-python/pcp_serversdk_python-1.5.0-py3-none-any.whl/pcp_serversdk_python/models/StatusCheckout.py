from enum import Enum


class StatusCheckout(str, Enum):
    OPEN = "OPEN"
    PENDING_COMPLETION = "PENDING_COMPLETION"
    COMPLETED = "COMPLETED"
    BILLED = "BILLED"
    CHARGEBACKED = "CHARGEBACKED"
    DELETED = "DELETED"
