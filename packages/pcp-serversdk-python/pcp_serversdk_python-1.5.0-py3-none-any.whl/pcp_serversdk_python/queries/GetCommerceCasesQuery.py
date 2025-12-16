from dataclasses import dataclass, field
from typing import Optional

from ..models import PaymentChannel, StatusCheckout


@dataclass
class GetCommerceCasesQuery:
    offset: Optional[int] = None
    size: Optional[int] = None
    fromDate: Optional[str] = None
    toDate: Optional[str] = None
    commerceCaseId: Optional[str] = None
    merchantReference: Optional[str] = None
    merchantCustomerId: Optional[str] = None
    includeCheckoutStatus: Optional[list[StatusCheckout]] = field(default_factory=list)
    includePaymentChannel: Optional[list[PaymentChannel]] = field(default_factory=list)

    # Setters
    def set_offset(self, offset: int) -> "GetCommerceCasesQuery":
        self.offset = offset
        return self

    def set_size(self, size: int) -> "GetCommerceCasesQuery":
        self.size = size
        return self

    def set_from_date(self, fromDate: str) -> "GetCommerceCasesQuery":
        self.fromDate = fromDate
        return self

    def set_to_date(self, toDate: str) -> "GetCommerceCasesQuery":
        self.toDate = toDate
        return self

    def set_commerce_case_id(self, commerceCaseId: str) -> "GetCommerceCasesQuery":
        self.commerceCaseId = commerceCaseId
        return self

    def set_merchant_reference(self, merchantReference: str) -> "GetCommerceCasesQuery":
        self.merchantReference = merchantReference
        return self

    def set_merchant_customer_id(
        self, merchantCustomerId: str
    ) -> "GetCommerceCasesQuery":
        self.merchantCustomerId = merchantCustomerId
        return self

    def set_include_checkout_status(
        self, includeCheckoutStatus: list[StatusCheckout]
    ) -> "GetCommerceCasesQuery":
        self.includeCheckoutStatus = includeCheckoutStatus
        return self

    def set_include_payment_channel(
        self, includePaymentChannel: list[PaymentChannel]
    ) -> "GetCommerceCasesQuery":
        self.includePaymentChannel = includePaymentChannel
        return self

    # Getters
    def get_offset(self) -> Optional[int]:
        return self.offset

    def get_size(self) -> Optional[int]:
        return self.size

    def get_from_date(self) -> Optional[str]:
        return self.fromDate

    def get_to_date(self) -> Optional[str]:
        return self.toDate

    def get_commerce_case_id(self) -> Optional[str]:
        return self.commerceCaseId

    def get_merchant_reference(self) -> Optional[str]:
        return self.merchantReference

    def get_merchant_customer_id(self) -> Optional[str]:
        return self.merchantCustomerId

    def get_include_checkout_status(self) -> list[StatusCheckout]:
        return self.includeCheckoutStatus

    def get_include_payment_channel(self) -> list[PaymentChannel]:
        return self.includePaymentChannel

    def to_query_map(self) -> dict[str, str]:
        query = {}

        if self.offset is not None:
            query["offset"] = str(self.offset)
        if self.size is not None:
            query["size"] = str(self.size)
        if self.fromDate is not None:
            query["fromDate"] = self.fromDate
        if self.toDate is not None:
            query["toDate"] = self.toDate
        if self.commerceCaseId is not None:
            query["commerceCaseId"] = self.commerceCaseId
        if self.merchantReference is not None:
            query["merchantReference"] = self.merchantReference
        if self.merchantCustomerId is not None:
            query["merchantCustomerId"] = self.merchantCustomerId
        if self.includeCheckoutStatus:
            query["includeCheckoutStatus"] = ",".join(
                status.name for status in self.includeCheckoutStatus
            )
        if self.includePaymentChannel:
            query["includePaymentChannel"] = ",".join(
                channel.name for channel in self.includePaymentChannel
            )

        return query
