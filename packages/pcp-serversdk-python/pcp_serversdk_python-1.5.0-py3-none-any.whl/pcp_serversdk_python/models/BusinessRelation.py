from enum import Enum


class BusinessRelation(Enum):
    """Enum for business relation type.

    Mandatory for the following payment methods:
    * 3390 - PAYONE Secured Invoice
    * 3391 - PAYONE Secured Installment
    * 3392 - PAYONE Secured Direct Debit
    """

    B2C = "B2C"  # Indicates business to consumer
    B2B = "B2B"  # Indicates business to business
