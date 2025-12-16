from enum import Enum


class DeliverType(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
