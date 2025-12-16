from enum import Enum


class CardOnFileRecurringFrequency(str, Enum):
    YEARLY = "Yearly"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"
    WEEKLY = "Weekly"
    DAILY = "Daily"
