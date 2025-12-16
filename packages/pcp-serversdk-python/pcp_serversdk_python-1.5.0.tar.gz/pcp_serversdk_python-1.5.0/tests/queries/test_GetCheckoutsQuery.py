from pcp_serversdk_python.models import (
    ExtendedCheckoutStatus,
    PaymentChannel,
    StatusCheckout,
)
from pcp_serversdk_python.queries import GetCheckoutsQuery


def testToQueryMap():
    query = GetCheckoutsQuery()
    query.set_offset(1)
    query.set_size(10)
    query.set_from_date("2021-01-01")
    query.set_to_date("2021-01-31")
    query.set_from_checkout_amount(100)
    query.set_to_checkout_amount(200)
    query.set_from_open_amount(50)
    query.set_to_open_amount(150)
    query.set_from_collected_amount(10)
    query.set_to_collected_amount(20)
    query.set_from_cancelled_amount(5)
    query.set_to_cancelled_amount(15)
    query.set_from_refund_amount(1)
    query.set_to_refund_amount(2)
    query.set_from_chargeback_amount(100)
    query.set_to_chargeback_amount(200)
    query.set_checkout_id("123456")
    query.set_merchant_reference("7890")
    query.set_merchant_customer_id("1234")
    query.set_include_payment_product_id([12, 456])
    query.set_include_checkout_status(
        [StatusCheckout.BILLED, StatusCheckout.CHARGEBACKED]
    )
    query.set_include_extended_checkout_status(
        [ExtendedCheckoutStatus.OPEN, ExtendedCheckoutStatus.DELETED]
    )
    query.set_include_payment_channel([PaymentChannel.ECOMMERCE, PaymentChannel.POS])
    query.set_payment_reference("1234")
    query.set_payment_id("5678")
    query.set_first_name("John")
    query.set_surname("Doe")
    query.set_email("john.doe@example.com")
    query.set_phone_number("1234567890")
    query.set_date_of_birth("1980-01-01")
    query.set_company_information("Company Inc.")
    query.set_terminal_id("1234")
    query.set_reporting_token("5678")

    query_map = query.to_query_map()

    assert query_map.get("offset") == "1"
    assert query_map.get("size") == "10"
    assert query_map.get("fromDate") == "2021-01-01"
    assert query_map.get("toDate") == "2021-01-31"
    assert query_map.get("fromCheckoutAmount") == "100"
    assert query_map.get("toCheckoutAmount") == "200"
    assert query_map.get("fromOpenAmount") == "50"
    assert query_map.get("toOpenAmount") == "150"
    assert query_map.get("fromCollectedAmount") == "10"
    assert query_map.get("toCollectedAmount") == "20"
    assert query_map.get("fromCancelledAmount") == "5"
    assert query_map.get("toCancelledAmount") == "15"
    assert query_map.get("fromRefundAmount") == "1"
    assert query_map.get("toRefundAmount") == "2"
    assert query_map.get("fromChargebackAmount") == "100"
    assert query_map.get("toChargebackAmount") == "200"
    assert query_map.get("checkoutId") == "123456"
    assert query_map.get("merchantReference") == "7890"
    assert query_map.get("merchantCustomerId") == "1234"
    assert query_map.get("includePaymentProductId") == "12,456"
    assert query_map.get("includeCheckoutStatus") == "BILLED,CHARGEBACKED"
    assert query_map.get("includeExtendedCheckoutStatus") == "OPEN,DELETED"
    assert query_map.get("includePaymentChannel") == "ECOMMERCE,POS"
    assert query_map.get("paymentReference") == "1234"
    assert query_map.get("paymentId") == "5678"
    assert query_map.get("firstName") == "John"
    assert query_map.get("surname") == "Doe"
    assert query_map.get("email") == "john.doe@example.com"
    assert query_map.get("phoneNumber") == "1234567890"
    assert query_map.get("dateOfBirth") == "1980-01-01"
    assert query_map.get("companyInformation") == "Company Inc."
    assert query_map.get("terminalId") == "1234"
    assert query_map.get("reportingToken") == "5678"


def testGetters():
    query = GetCheckoutsQuery()
    query.set_offset(1)
    query.set_size(10)
    query.set_from_date("2021-01-01")
    query.set_to_date("2021-01-31")
    query.set_from_checkout_amount(100)
    query.set_to_checkout_amount(200)
    query.set_from_open_amount(50)
    query.set_to_open_amount(150)
    query.set_from_collected_amount(10)
    query.set_to_collected_amount(20)
    query.set_from_cancelled_amount(5)
    query.set_to_cancelled_amount(15)
    query.set_from_refund_amount(1)
    query.set_to_refund_amount(2)
    query.set_from_chargeback_amount(100)
    query.set_to_chargeback_amount(200)
    query.set_checkout_id("123456")
    query.set_merchant_reference("7890")
    query.set_merchant_customer_id("1234")
    query.set_include_payment_product_id([12, 456])
    query.set_include_checkout_status(
        [StatusCheckout.BILLED, StatusCheckout.CHARGEBACKED]
    )
    query.set_include_extended_checkout_status(
        [ExtendedCheckoutStatus.OPEN, ExtendedCheckoutStatus.DELETED]
    )
    query.set_include_payment_channel([PaymentChannel.ECOMMERCE, PaymentChannel.POS])
    query.set_payment_reference("1234")
    query.set_payment_id("5678")
    query.set_first_name("John")
    query.set_surname("Doe")
    query.set_email("john.doe@example.com")
    query.set_phone_number("1234567890")
    query.set_date_of_birth("1980-01-01")
    query.set_company_information("Company Inc.")
    query.set_terminal_id("1234")
    query.set_reporting_token("5678")

    assert query.get_offset() == 1
    assert query.get_size() == 10
    assert query.get_from_date() == "2021-01-01"
    assert query.get_to_date() == "2021-01-31"
    assert query.get_from_checkout_amount() == 100
    assert query.get_to_checkout_amount() == 200
    assert query.get_from_open_amount() == 50
    assert query.get_to_open_amount() == 150
    assert query.get_from_collected_amount() == 10
    assert query.get_to_collected_amount() == 20
    assert query.get_from_cancelled_amount() == 5
    assert query.get_to_cancelled_amount() == 15
    assert query.get_from_refund_amount() == 1
    assert query.get_to_refund_amount() == 2
    assert query.get_from_chargeback_amount() == 100
    assert query.get_to_chargeback_amount() == 200
    assert query.get_checkout_id() == "123456"
    assert query.get_merchant_reference() == "7890"
    assert query.get_merchant_customer_id() == "1234"
    assert query.get_include_payment_product_id() == [12, 456]
    assert query.get_include_checkout_status() == [
        StatusCheckout.BILLED,
        StatusCheckout.CHARGEBACKED,
    ]
    assert query.get_include_extended_checkout_status() == [
        ExtendedCheckoutStatus.OPEN,
        ExtendedCheckoutStatus.DELETED,
    ]
    assert query.get_include_payment_channel() == [
        PaymentChannel.ECOMMERCE,
        PaymentChannel.POS,
    ]
    assert query.get_payment_reference() == "1234"
    assert query.get_payment_id() == "5678"
    assert query.get_first_name() == "John"
    assert query.get_surname() == "Doe"
    assert query.get_email() == "john.doe@example.com"
    assert query.get_phone_number() == "1234567890"
    assert query.get_date_of_birth() == "1980-01-01"
    assert query.get_company_information() == "Company Inc."
    assert query.get_terminal_id() == "1234"
    assert query.get_reporting_token() == "5678"


def testNulls():
    query = GetCheckoutsQuery()
    query_map = query.to_query_map()

    assert len(query_map) == 0
