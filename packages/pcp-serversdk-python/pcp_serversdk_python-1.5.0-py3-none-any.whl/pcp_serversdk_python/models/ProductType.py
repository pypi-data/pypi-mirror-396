from enum import Enum


class ProductType(str, Enum):
    GOODS = "GOODS"
    SHIPMENT = "SHIPMENT"
    HANDLING_FEE = "HANDLING_FEE"
    DISCOUNT = "DISCOUNT"
