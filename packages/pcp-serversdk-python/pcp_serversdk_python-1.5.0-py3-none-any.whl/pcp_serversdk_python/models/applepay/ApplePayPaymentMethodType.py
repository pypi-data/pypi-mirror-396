from enum import Enum


class ApplePayPaymentMethodType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    PREPAID = "prepaid"
    STORE = "store"
