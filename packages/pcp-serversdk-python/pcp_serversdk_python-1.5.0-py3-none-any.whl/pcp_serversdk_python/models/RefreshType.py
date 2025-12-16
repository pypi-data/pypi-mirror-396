from enum import Enum


class RefreshType(str, Enum):
    """The refreshType refers to the type of the payment status refresh.

    - `PAYMENT_EVENTS`: Refresh the payment status of the payment and return the events.
      This is a synchronization of the payment status with the payment platform.
      This can be used in case of any possible inconsistencies between the commerce platform
      and the payment platform.

    - `PAYMENT_PROVIDER_DETAILS`: Refresh the payment status of the payment and return the
      payment provider details. This is a synchronization of the payment with the external
      payment provider. The current use case is to update the customer status of a transaction
      using PAYONE Buy Now, Pay Later (BNPL) with the external provider Payla.
    """

    PAYMENT_EVENTS = "PAYMENT_EVENTS"
    PAYMENT_PROVIDER_DETAILS = "PAYMENT_PROVIDER_DETAILS"
