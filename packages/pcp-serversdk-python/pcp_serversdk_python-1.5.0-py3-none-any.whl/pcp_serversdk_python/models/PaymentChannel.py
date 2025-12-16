from enum import Enum


class PaymentChannel(str, Enum):
    ECOMMERCE = "ECOMMERCE"
    POS = "POS"
