import json
from dataclasses import asdict

import httpx
import pytest

from pcp_serversdk_python.CommunicatorConfiguration import CommunicatorConfiguration
from pcp_serversdk_python.endpoints import PaymentInformationApiClient
from pcp_serversdk_python.models import (
    AmountOfMoney,
    PaymentChannel,
    PaymentInformationRefundRequest,
    PaymentInformationRefundResponse,
    PaymentInformationRequest,
    PaymentInformationResponse,
    PaymentReferences,
    PaymentType,
)


@pytest.fixture
def payment_information_api_client():
    config = CommunicatorConfiguration("apiKey", "apiSecret", "https://test.com")
    return PaymentInformationApiClient(config)


@pytest.fixture
def mock_httpx_client(mocker):
    # Mock httpx.AsyncClient and its methods
    mock_client = mocker.patch(
        "httpx.AsyncClient",
        autospec=True,
    )
    return mock_client


@pytest.mark.asyncio
async def test_create_payment_information(
    payment_information_api_client, mock_httpx_client
):
    expected_response = PaymentInformationResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(201, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await payment_information_api_client.create_payment_information(
        "merchant_id",
        "commerce_case_id",
        "checkout_id",
        create_payment_information(),
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_get_payment_information(
    payment_information_api_client, mock_httpx_client
):
    expected_response = PaymentInformationResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await payment_information_api_client.get_payment_information(
        "merchant_id", "commerce_case_id", "checkout_id", "payment_information_id"
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_refund_payment_information(
    payment_information_api_client, mock_httpx_client
):
    expected_response = PaymentInformationRefundResponse(
        payment=None,
        paymentExecutionId=None,
    )

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    payload = PaymentInformationRefundRequest(
        amountOfMoney=AmountOfMoney(amount=1000, currencyCode="EUR"),
        references=PaymentReferences(merchantReference="refund-123"),
        accountHolder="John Doe",
    )

    response = await payment_information_api_client.refund_payment_information(
        "merchant_id",
        "commerce_case_id",
        "checkout_id",
        "payment_information_id",
        payload,
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_refund_payment_information_with_invalid_payment_information_id(
    payment_information_api_client,
):
    with pytest.raises(ValueError):
        payload = PaymentInformationRefundRequest(
            amountOfMoney=AmountOfMoney(amount=1000, currencyCode="EUR")
        )
        await payment_information_api_client.refund_payment_information(
            "merchant_id", "commerce_case_id", "checkout_id", "", payload
        )


@pytest.mark.asyncio
async def test_create_payment_information_with_invalid_merchant_id(
    payment_information_api_client,
):
    with pytest.raises(ValueError):
        await payment_information_api_client.create_payment_information(
            "", "commerce_case_id", "checkout_id", create_payment_information()
        )


@pytest.mark.asyncio
async def test_create_payment_information_with_invalid_commerce_case_id(
    payment_information_api_client,
):
    with pytest.raises(ValueError):
        await payment_information_api_client.create_payment_information(
            "merchant_id", "", "checkout_id", create_payment_information()
        )


@pytest.mark.asyncio
async def test_create_payment_information_with_invalid_checkout_id(
    payment_information_api_client,
):
    with pytest.raises(ValueError):
        await payment_information_api_client.create_payment_information(
            "merchant_id", "commerce_case_id", "", create_payment_information()
        )


@pytest.mark.asyncio
async def test_get_payment_information_with_invalid_payment_information_id(
    payment_information_api_client,
):
    with pytest.raises(ValueError):
        await payment_information_api_client.get_payment_information(
            "merchant_id", "commerce_case_id", "checkout_id", ""
        )


def create_payment_information():
    return PaymentInformationRequest(
        amountOfMoney=AmountOfMoney(
            amount=1000,
            currencyCode="EUR",
        ),
        type=PaymentType.Capture,
        paymentChannel=PaymentChannel.ECOMMERCE,
        paymentProductId=1,
        merchantReference="merchantReference",
    )
