import json
from dataclasses import asdict

import httpx
import pytest

from pcp_serversdk_python.CommunicatorConfiguration import CommunicatorConfiguration
from pcp_serversdk_python.endpoints import (
    PaymentExecutionApiClient,
)
from pcp_serversdk_python.models import (
    CancelPaymentRequest,
    CancelPaymentResponse,
    CapturePaymentRequest,
    CapturePaymentResponse,
    CompletePaymentProduct840SpecificInput,
    CompletePaymentRequest,
    CompletePaymentResponse,
    CompleteRedirectPaymentMethodSpecificInput,
    CreatePaymentResponse,
    PausePaymentRequest,
    PausePaymentResponse,
    PaymentExecution,
    PaymentExecutionRequest,
    RefreshPaymentRequest,
    RefundPaymentResponse,
    RefundRequest,
)


@pytest.fixture
def payment_execution_api_client():
    config = CommunicatorConfiguration("apiKey", "apiSecret", "https://test.com")
    return PaymentExecutionApiClient(config)


@pytest.fixture
def mock_httpx_client(mocker):
    # Mock httpx.AsyncClient and its methods
    mock_client = mocker.patch(
        "httpx.AsyncClient",
        autospec=True,
    )
    return mock_client


@pytest.mark.asyncio
async def test_create_payment(payment_execution_api_client, mock_httpx_client):
    expected_response = CreatePaymentResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await payment_execution_api_client.create_payment(
        "merchant_id", "commerce_case_id", "checkout_id", PaymentExecutionRequest()
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_capture_payment(payment_execution_api_client, mock_httpx_client):
    expected_response = CapturePaymentResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await payment_execution_api_client.capture_payment(
        "merchant_id",
        "commerce_case_id",
        "checkout_id",
        "payment_execution_id",
        CapturePaymentRequest(),
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_cancel_payment(payment_execution_api_client, mock_httpx_client):
    expected_response = CancelPaymentResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await payment_execution_api_client.cancel_payment(
        "merchant_id",
        "commerce_case_id",
        "checkout_id",
        "payment_execution_id",
        CancelPaymentRequest(),
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_refund_payment(payment_execution_api_client, mock_httpx_client):
    expected_response = RefundPaymentResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await payment_execution_api_client.refund_payment(
        "merchant_id",
        "commerce_case_id",
        "checkout_id",
        "payment_execution_id",
        RefundRequest(),
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_complete_payment(payment_execution_api_client, mock_httpx_client):
    expected_response = CompletePaymentResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    payload = CompletePaymentRequest()
    redirect_input = CompleteRedirectPaymentMethodSpecificInput()
    product840_input = CompletePaymentProduct840SpecificInput(
        action="CONFIRM_ORDER_STATUS",
        javaScriptSdkFlow=True,
    )
    redirect_input.paymentProduct840SpecificInput = product840_input
    payload.redirectPaymentMethodSpecificInput = redirect_input

    response = await payment_execution_api_client.complete_payment(
        "merchant_id",
        "commerce_case_id",
        "checkout_id",
        "payment_execution_id",
        payload,
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_pause_payment(payment_execution_api_client, mock_httpx_client):
    expected_response = PausePaymentResponse(status=None)

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await payment_execution_api_client.pause_payment(
        "merchant_id",
        "commerce_case_id",
        "checkout_id",
        "payment_execution_id",
        PausePaymentRequest(refreshType=None),
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_refresh_payment(payment_execution_api_client, mock_httpx_client):
    expected_response = PaymentExecution()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await payment_execution_api_client.refresh_payment(
        "merchant_id",
        "commerce_case_id",
        "checkout_id",
        "payment_execution_id",
        RefreshPaymentRequest(refreshType=None),
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_pause_payment_with_invalid_payment_execution_id(
    payment_execution_api_client,
):
    with pytest.raises(ValueError):
        await payment_execution_api_client.pause_payment(
            "merchant_id",
            "commerce_case_id",
            "checkout_id",
            "",
            PausePaymentRequest(refreshType=None),
        )


@pytest.mark.asyncio
async def test_refresh_payment_with_invalid_payment_execution_id(
    payment_execution_api_client,
):
    with pytest.raises(ValueError):
        await payment_execution_api_client.refresh_payment(
            "merchant_id",
            "commerce_case_id",
            "checkout_id",
            "",
            RefreshPaymentRequest(refreshType=None),
        )


@pytest.mark.asyncio
async def test_capture_payment_with_invalid_payment_execution_id(
    payment_execution_api_client,
):
    with pytest.raises(ValueError):
        await payment_execution_api_client.capture_payment(
            "merchant_id",
            "commerce_case_id",
            "checkout_id",
            "",
            CapturePaymentRequest(),
        )


@pytest.mark.asyncio
async def test_create_payment_with_invalid_merchant_id(payment_execution_api_client):
    with pytest.raises(ValueError):
        await payment_execution_api_client.create_payment(
            "", "commerce_case_id", "checkout_id", PaymentExecutionRequest()
        )


@pytest.mark.asyncio
async def test_create_payment_with_invalid_commerce_case_id(
    payment_execution_api_client,
):
    with pytest.raises(ValueError):
        await payment_execution_api_client.create_payment(
            "merchant_id", "", "checkout_id", PaymentExecutionRequest()
        )


@pytest.mark.asyncio
async def test_create_payment_with_invalid_checkout_id(payment_execution_api_client):
    with pytest.raises(ValueError):
        await payment_execution_api_client.create_payment(
            "merchant_id", "commerce_case_id", "", PaymentExecutionRequest()
        )
