from enum import Enum


class TransactionChannel(str, Enum):
    ECOMMERCE = "ECOMMERCE"
    MOTO = "MOTO"
