from pcp_serversdk_python.models import PaymentChannel, StatusCheckout
from pcp_serversdk_python.queries import GetCommerceCasesQuery


def testToQueryMap():
    query = GetCommerceCasesQuery()
    query.set_offset(1)
    query.set_size(10)
    query.set_from_date("2021-01-01")
    query.set_to_date("2021-01-31")
    query.set_commerce_case_id("123456")
    query.set_merchant_reference("7890")
    query.set_merchant_customer_id("1234")
    query.set_include_checkout_status(
        [StatusCheckout.BILLED, StatusCheckout.CHARGEBACKED]
    )
    query.set_include_payment_channel([PaymentChannel.ECOMMERCE, PaymentChannel.POS])

    queryMap = query.to_query_map()

    assert queryMap.get("offset") == "1"
    assert queryMap.get("size") == "10"
    assert queryMap.get("fromDate") == "2021-01-01"
    assert queryMap.get("toDate") == "2021-01-31"
    assert queryMap.get("commerceCaseId") == "123456"
    assert queryMap.get("merchantReference") == "7890"
    assert queryMap.get("merchantCustomerId") == "1234"
    assert queryMap.get("includeCheckoutStatus") == "BILLED,CHARGEBACKED"
    assert queryMap.get("includePaymentChannel") == "ECOMMERCE,POS"


def testGetters():
    query = GetCommerceCasesQuery()
    query.set_offset(1)
    query.set_size(10)
    query.set_from_date("2021-01-01")
    query.set_to_date("2021-01-31")
    query.set_commerce_case_id("123456")
    query.set_merchant_reference("7890")
    query.set_merchant_customer_id("1234")
    query.set_include_checkout_status(
        [StatusCheckout.BILLED, StatusCheckout.CHARGEBACKED]
    )
    query.set_include_payment_channel([PaymentChannel.ECOMMERCE, PaymentChannel.POS])

    assert query.get_offset() == 1
    assert query.get_size() == 10
    assert query.get_from_date() == "2021-01-01"
    assert query.get_to_date() == "2021-01-31"
    assert query.get_commerce_case_id() == "123456"
    assert query.get_merchant_reference() == "7890"
    assert query.get_merchant_customer_id() == "1234"
    assert query.get_include_checkout_status() == [
        StatusCheckout.BILLED,
        StatusCheckout.CHARGEBACKED,
    ]
    assert query.get_include_payment_channel() == [
        PaymentChannel.ECOMMERCE,
        PaymentChannel.POS,
    ]


def testNulls():
    query = GetCommerceCasesQuery()
    queryMap = query.to_query_map()

    assert len(queryMap) == 0
