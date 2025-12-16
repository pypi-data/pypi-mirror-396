from dataclasses import dataclass, field
from typing import Optional

# Import enums and other necessary classes
from ..models import ExtendedCheckoutStatus, PaymentChannel, StatusCheckout


@dataclass
class GetCheckoutsQuery:
    offset: Optional[int] = None
    size: Optional[int] = None
    fromDate: Optional[str] = None
    toDate: Optional[str] = None
    fromCheckoutAmount: Optional[int] = None
    toCheckoutAmount: Optional[int] = None
    fromOpenAmount: Optional[int] = None
    toOpenAmount: Optional[int] = None
    fromCollectedAmount: Optional[int] = None
    toCollectedAmount: Optional[int] = None
    fromCancelledAmount: Optional[int] = None
    toCancelledAmount: Optional[int] = None
    fromRefundAmount: Optional[int] = None
    toRefundAmount: Optional[int] = None
    fromChargebackAmount: Optional[int] = None
    toChargebackAmount: Optional[int] = None
    checkoutId: Optional[str] = None
    merchantReference: Optional[str] = None
    merchantCustomerId: Optional[str] = None
    includePaymentProductId: Optional[list[int]] = field(default_factory=list)
    includeCheckoutStatus: Optional[list[StatusCheckout]] = field(default_factory=list)
    includeExtendedCheckoutStatus: Optional[list[ExtendedCheckoutStatus]] = field(
        default_factory=list
    )
    includePaymentChannel: Optional[list[PaymentChannel]] = field(default_factory=list)
    paymentReference: Optional[str] = None
    paymentId: Optional[str] = None
    firstName: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    dateOfBirth: Optional[str] = None
    companyInformation: Optional[str] = None
    terminalId: Optional[str] = None
    reportingToken: Optional[str] = None

    # Setters (already provided)

    def set_offset(self, offset: int) -> "GetCheckoutsQuery":
        self.offset = offset
        return self

    def set_size(self, size: int) -> "GetCheckoutsQuery":
        self.size = size
        return self

    def set_from_date(self, fromDate: str) -> "GetCheckoutsQuery":
        self.fromDate = fromDate
        return self

    def set_to_date(self, toDate: str) -> "GetCheckoutsQuery":
        self.toDate = toDate
        return self

    def set_from_checkout_amount(self, fromCheckoutAmount: int) -> "GetCheckoutsQuery":
        self.fromCheckoutAmount = fromCheckoutAmount
        return self

    def set_to_checkout_amount(self, toCheckoutAmount: int) -> "GetCheckoutsQuery":
        self.toCheckoutAmount = toCheckoutAmount
        return self

    def set_from_open_amount(self, fromOpenAmount: int) -> "GetCheckoutsQuery":
        self.fromOpenAmount = fromOpenAmount
        return self

    def set_to_open_amount(self, toOpenAmount: int) -> "GetCheckoutsQuery":
        self.toOpenAmount = toOpenAmount
        return self

    def set_from_collected_amount(
        self, fromCollectedAmount: int
    ) -> "GetCheckoutsQuery":
        self.fromCollectedAmount = fromCollectedAmount
        return self

    def set_to_collected_amount(self, toCollectedAmount: int) -> "GetCheckoutsQuery":
        self.toCollectedAmount = toCollectedAmount
        return self

    def set_from_cancelled_amount(
        self, fromCancelledAmount: int
    ) -> "GetCheckoutsQuery":
        self.fromCancelledAmount = fromCancelledAmount
        return self

    def set_to_cancelled_amount(self, toCancelledAmount: int) -> "GetCheckoutsQuery":
        self.toCancelledAmount = toCancelledAmount
        return self

    def set_from_refund_amount(self, fromRefundAmount: int) -> "GetCheckoutsQuery":
        self.fromRefundAmount = fromRefundAmount
        return self

    def set_to_refund_amount(self, toRefundAmount: int) -> "GetCheckoutsQuery":
        self.toRefundAmount = toRefundAmount
        return self

    def set_from_chargeback_amount(
        self, fromChargebackAmount: int
    ) -> "GetCheckoutsQuery":
        self.fromChargebackAmount = fromChargebackAmount
        return self

    def set_to_chargeback_amount(self, toChargebackAmount: int) -> "GetCheckoutsQuery":
        self.toChargebackAmount = toChargebackAmount
        return self

    def set_checkout_id(self, checkoutId: str) -> "GetCheckoutsQuery":
        self.checkoutId = checkoutId
        return self

    def set_merchant_reference(self, merchantReference: str) -> "GetCheckoutsQuery":
        self.merchantReference = merchantReference
        return self

    def set_merchant_customer_id(self, merchantCustomerId: str) -> "GetCheckoutsQuery":
        self.merchantCustomerId = merchantCustomerId
        return self

    def set_include_payment_product_id(
        self, includePaymentProductId: list[int]
    ) -> "GetCheckoutsQuery":
        self.includePaymentProductId = includePaymentProductId
        return self

    def set_include_checkout_status(
        self, includeCheckoutStatus: list[StatusCheckout]
    ) -> "GetCheckoutsQuery":
        self.includeCheckoutStatus = includeCheckoutStatus
        return self

    def set_include_extended_checkout_status(
        self, includeExtendedCheckoutStatus: list[ExtendedCheckoutStatus]
    ) -> "GetCheckoutsQuery":
        self.includeExtendedCheckoutStatus = includeExtendedCheckoutStatus
        return self

    def set_include_payment_channel(
        self, includePaymentChannel: list[PaymentChannel]
    ) -> "GetCheckoutsQuery":
        self.includePaymentChannel = includePaymentChannel
        return self

    def set_payment_reference(self, paymentReference: str) -> "GetCheckoutsQuery":
        self.paymentReference = paymentReference
        return self

    def set_payment_id(self, paymentId: str) -> "GetCheckoutsQuery":
        self.paymentId = paymentId
        return self

    def set_first_name(self, firstName: str) -> "GetCheckoutsQuery":
        self.firstName = firstName
        return self

    def set_surname(self, surname: str) -> "GetCheckoutsQuery":
        self.surname = surname
        return self

    def set_email(self, email: str) -> "GetCheckoutsQuery":
        self.email = email
        return self

    def set_phone_number(self, phoneNumber: str) -> "GetCheckoutsQuery":
        self.phoneNumber = phoneNumber
        return self

    def set_date_of_birth(self, dateOfBirth: str) -> "GetCheckoutsQuery":
        self.dateOfBirth = dateOfBirth
        return self

    def set_company_information(self, companyInformation: str) -> "GetCheckoutsQuery":
        self.companyInformation = companyInformation
        return self

    def set_terminal_id(self, terminalId: str) -> "GetCheckoutsQuery":
        self.terminalId = terminalId
        return self

    def set_reporting_token(self, reportingToken: str) -> "GetCheckoutsQuery":
        self.reportingToken = reportingToken
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

    def get_from_checkout_amount(self) -> Optional[int]:
        return self.fromCheckoutAmount

    def get_to_checkout_amount(self) -> Optional[int]:
        return self.toCheckoutAmount

    def get_from_open_amount(self) -> Optional[int]:
        return self.fromOpenAmount

    def get_to_open_amount(self) -> Optional[int]:
        return self.toOpenAmount

    def get_from_collected_amount(self) -> Optional[int]:
        return self.fromCollectedAmount

    def get_to_collected_amount(self) -> Optional[int]:
        return self.toCollectedAmount

    def get_from_cancelled_amount(self) -> Optional[int]:
        return self.fromCancelledAmount

    def get_to_cancelled_amount(self) -> Optional[int]:
        return self.toCancelledAmount

    def get_from_refund_amount(self) -> Optional[int]:
        return self.fromRefundAmount

    def get_to_refund_amount(self) -> Optional[int]:
        return self.toRefundAmount

    def get_from_chargeback_amount(self) -> Optional[int]:
        return self.fromChargebackAmount

    def get_to_chargeback_amount(self) -> Optional[int]:
        return self.toChargebackAmount

    def get_checkout_id(self) -> Optional[str]:
        return self.checkoutId

    def get_merchant_reference(self) -> Optional[str]:
        return self.merchantReference

    def get_merchant_customer_id(self) -> Optional[str]:
        return self.merchantCustomerId

    def get_include_payment_product_id(self) -> list[int]:
        return self.includePaymentProductId

    def get_include_checkout_status(self) -> list[StatusCheckout]:
        return self.includeCheckoutStatus

    def get_include_extended_checkout_status(self) -> list[ExtendedCheckoutStatus]:
        return self.includeExtendedCheckoutStatus

    def get_include_payment_channel(self) -> list[PaymentChannel]:
        return self.includePaymentChannel

    def get_payment_reference(self) -> Optional[str]:
        return self.paymentReference

    def get_payment_id(self) -> Optional[str]:
        return self.paymentId

    def get_first_name(self) -> Optional[str]:
        return self.firstName

    def get_surname(self) -> Optional[str]:
        return self.surname

    def get_email(self) -> Optional[str]:
        return self.email

    def get_phone_number(self) -> Optional[str]:
        return self.phoneNumber

    def get_date_of_birth(self) -> Optional[str]:
        return self.dateOfBirth

    def get_company_information(self) -> Optional[str]:
        return self.companyInformation

    def get_terminal_id(self) -> Optional[str]:
        return self.terminalId

    def get_reporting_token(self) -> Optional[str]:
        return self.reportingToken

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
        if self.fromCheckoutAmount is not None:
            query["fromCheckoutAmount"] = str(self.fromCheckoutAmount)
        if self.toCheckoutAmount is not None:
            query["toCheckoutAmount"] = str(self.toCheckoutAmount)
        if self.fromOpenAmount is not None:
            query["fromOpenAmount"] = str(self.fromOpenAmount)
        if self.toOpenAmount is not None:
            query["toOpenAmount"] = str(self.toOpenAmount)
        if self.fromCollectedAmount is not None:
            query["fromCollectedAmount"] = str(self.fromCollectedAmount)
        if self.toCollectedAmount is not None:
            query["toCollectedAmount"] = str(self.toCollectedAmount)
        if self.fromCancelledAmount is not None:
            query["fromCancelledAmount"] = str(self.fromCancelledAmount)
        if self.toCancelledAmount is not None:
            query["toCancelledAmount"] = str(self.toCancelledAmount)
        if self.fromRefundAmount is not None:
            query["fromRefundAmount"] = str(self.fromRefundAmount)
        if self.toRefundAmount is not None:
            query["toRefundAmount"] = str(self.toRefundAmount)
        if self.fromChargebackAmount is not None:
            query["fromChargebackAmount"] = str(self.fromChargebackAmount)
        if self.toChargebackAmount is not None:
            query["toChargebackAmount"] = str(self.toChargebackAmount)
        if self.checkoutId is not None:
            query["checkoutId"] = self.checkoutId
        if self.merchantReference is not None:
            query["merchantReference"] = self.merchantReference
        if self.merchantCustomerId is not None:
            query["merchantCustomerId"] = self.merchantCustomerId
        if self.includePaymentProductId:
            query["includePaymentProductId"] = ",".join(
                map(str, self.includePaymentProductId)
            )
        if self.includeCheckoutStatus:
            query["includeCheckoutStatus"] = ",".join(
                status.name for status in self.includeCheckoutStatus
            )
        if self.includeExtendedCheckoutStatus:
            query["includeExtendedCheckoutStatus"] = ",".join(
                status.name for status in self.includeExtendedCheckoutStatus
            )
        if self.includePaymentChannel:
            query["includePaymentChannel"] = ",".join(
                channel.name for channel in self.includePaymentChannel
            )
        if self.paymentReference is not None:
            query["paymentReference"] = self.paymentReference
        if self.paymentId is not None:
            query["paymentId"] = self.paymentId
        if self.firstName is not None:
            query["firstName"] = self.firstName
        if self.surname is not None:
            query["surname"] = self.surname
        if self.email is not None:
            query["email"] = self.email
        if self.phoneNumber is not None:
            query["phoneNumber"] = self.phoneNumber
        if self.dateOfBirth is not None:
            query["dateOfBirth"] = self.dateOfBirth
        if self.companyInformation is not None:
            query["companyInformation"] = self.companyInformation
        if self.terminalId is not None:
            query["terminalId"] = self.terminalId
        if self.reportingToken is not None:
            query["reportingToken"] = self.reportingToken

        return query
