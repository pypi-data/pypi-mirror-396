from enum import Enum


class UnscheduledCardOnFileRequestor(str, Enum):
    MERCHANT_INITIATED = "merchantInitiated"
    CARDHOLDER_INITIATED = "cardholderInitiated"
