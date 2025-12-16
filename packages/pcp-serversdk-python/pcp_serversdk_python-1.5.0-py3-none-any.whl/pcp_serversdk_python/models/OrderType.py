from enum import Enum


class OrderType(str, Enum):
    Full = "FULL"
    Partial = "PARTIAL"
