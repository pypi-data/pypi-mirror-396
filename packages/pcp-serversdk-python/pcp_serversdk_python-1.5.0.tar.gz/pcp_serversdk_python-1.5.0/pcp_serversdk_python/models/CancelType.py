from enum import Enum


class CancelType(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
