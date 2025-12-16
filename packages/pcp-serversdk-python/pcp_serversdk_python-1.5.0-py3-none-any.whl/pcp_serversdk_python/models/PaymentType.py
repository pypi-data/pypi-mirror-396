from enum import Enum


class PaymentType(str, Enum):
    Sale = "SALE"
    Reservation = "RESERVATION"
    Capture = "CAPTURE"
    Refund = "REFUND"
    Reversal = "REVERSAL"
    Chargeback = "CHARGEBACK"
    ChargebackReversal = "CHARGEBACK_REVERSAL"
    CreditNote = "CREDIT_NOTE"
    DebitNote = "DEBIT_NOTE"
