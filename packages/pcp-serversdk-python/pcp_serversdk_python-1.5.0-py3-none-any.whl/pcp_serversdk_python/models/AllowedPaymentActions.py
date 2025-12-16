from enum import Enum


class AllowedPaymentActions(str, Enum):
    OrderManagement = "ORDER_MANAGEMENT"
    PaymentExecution = "PAYMENT_EXECUTION"
