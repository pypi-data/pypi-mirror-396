import json
from dataclasses import asdict

import httpx
import pytest

from pcp_serversdk_python.CommunicatorConfiguration import CommunicatorConfiguration
from pcp_serversdk_python.endpoints import OrderManagementCheckoutActionsApiClient
from pcp_serversdk_python.models import (
    CancelRequest,
    CancelResponse,
    DeliverRequest,
    DeliverResponse,
    OrderRequest,
    OrderResponse,
    ReturnRequest,
    ReturnResponse,
)


@pytest.fixture
def order_management_checkout_actions_api_client():
    config = CommunicatorConfiguration("apiKey", "apiSecret", "https://test.com")
    return OrderManagementCheckoutActionsApiClient(config)


@pytest.fixture
def mock_httpx_client(mocker):
    # Mock httpx.AsyncClient and its methods
    mock_client = mocker.patch(
        "httpx.AsyncClient",
        autospec=True,
    )
    return mock_client


@pytest.mark.asyncio
async def test_run_create_order(
    order_management_checkout_actions_api_client, mock_httpx_client
):
    expected_response = OrderResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await order_management_checkout_actions_api_client.create_order(
        "merchant_id", "commerce_case_id", "checkout_id", OrderRequest()
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_run_deliver_order(
    order_management_checkout_actions_api_client, mock_httpx_client
):
    expected_response = DeliverResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await order_management_checkout_actions_api_client.deliver_order(
        "merchant_id", "commerce_case_id", "checkout_id", DeliverRequest()
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_run_return_order(
    order_management_checkout_actions_api_client, mock_httpx_client
):
    expected_response = ReturnResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await order_management_checkout_actions_api_client.return_order(
        "merchant_id", "commerce_case_id", "checkout_id", ReturnRequest()
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_run_cancel_order(
    order_management_checkout_actions_api_client, mock_httpx_client
):
    expected_response = CancelResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await order_management_checkout_actions_api_client.cancel_order(
        "merchant_id", "commerce_case_id", "checkout_id", CancelRequest()
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_run_create_order_no_merchant_id_error(
    order_management_checkout_actions_api_client,
):
    with pytest.raises(ValueError):
        await order_management_checkout_actions_api_client.create_order(
            "", "commerce_case_id", "checkout_id", OrderRequest()
        )


@pytest.mark.asyncio
async def test_run_create_order_no_commerce_case_id_error(
    order_management_checkout_actions_api_client,
):
    with pytest.raises(ValueError):
        await order_management_checkout_actions_api_client.create_order(
            "merchant_id", "", "checkout_id", OrderRequest()
        )


@pytest.mark.asyncio
async def test_run_create_order_no_checkout_id_error(
    order_management_checkout_actions_api_client,
):
    with pytest.raises(ValueError):
        await order_management_checkout_actions_api_client.create_order(
            "merchant_id", "commerce_case_id", "", OrderRequest()
        )
