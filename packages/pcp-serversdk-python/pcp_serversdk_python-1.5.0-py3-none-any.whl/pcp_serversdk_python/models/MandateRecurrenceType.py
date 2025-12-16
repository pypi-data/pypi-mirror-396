from enum import Enum


class MandateRecurrenceType(str, Enum):
    UNIQUE = "UNIQUE"
    RECURRING = "RECURRING"
