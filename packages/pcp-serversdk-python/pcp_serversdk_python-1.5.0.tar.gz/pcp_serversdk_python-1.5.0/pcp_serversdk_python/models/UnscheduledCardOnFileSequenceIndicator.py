from enum import Enum


class UnscheduledCardOnFileSequenceIndicator(str, Enum):
    FIRST = "first"
    SUBSEQUENT = "subsequent"
