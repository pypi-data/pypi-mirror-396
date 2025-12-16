from enum import Enum


class Network(str, Enum):
    MASTERCARD = "MASTERCARD"
    VISA = "VISA"
    AMEX = "AMEX"
    GIROCARD = "GIROCARD"
    DISCOVER = "DISCOVER"
    JCB = "JCB"
