import json
from dataclasses import asdict

import httpx
import pytest

from pcp_serversdk_python.CommunicatorConfiguration import CommunicatorConfiguration
from pcp_serversdk_python.endpoints import CommerceCaseApiClient
from pcp_serversdk_python.models import (
    CommerceCaseResponse,
    CreateCommerceCaseRequest,
    CreateCommerceCaseResponse,
    Customer,
)
from pcp_serversdk_python.queries import GetCommerceCasesQuery


@pytest.fixture
def commerce_case_api_client():
    config = CommunicatorConfiguration("apiKey", "apiSecret", "https://test.com")
    return CommerceCaseApiClient(config)


@pytest.fixture
def mock_httpx_client(mocker):
    # Mock httpx.AsyncClient and its methods
    mock_client = mocker.patch(
        "httpx.AsyncClient",
        autospec=True,
    )
    return mock_client


@pytest.mark.asyncio
async def test_create_commerce_case_request(
    commerce_case_api_client, mock_httpx_client
):
    expected_response = CreateCommerceCaseResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await commerce_case_api_client.create_commerce_case_request(
        "merchantId", CreateCommerceCaseRequest()
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_create_commerce_case_request_no_merchant_id_error(
    commerce_case_api_client,
):
    with pytest.raises(ValueError):
        await commerce_case_api_client.create_commerce_case_request(
            "", CreateCommerceCaseRequest()
        )


@pytest.mark.asyncio
async def test_get_commerce_case_request(commerce_case_api_client, mock_httpx_client):
    expected_response = CommerceCaseResponse()

    res = json.dumps(asdict(expected_response))

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await commerce_case_api_client.get_commerce_case_request(
        "merchantId", "commerceCaseId"
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_get_commerce_case_request_no_merchant_id_error(
    commerce_case_api_client,
):
    with pytest.raises(ValueError):
        await commerce_case_api_client.get_commerce_case_request("", "commerceCaseId")


@pytest.mark.asyncio
async def test_get_commerce_case_request_no_commerce_case_id_error(
    commerce_case_api_client,
):
    with pytest.raises(ValueError):
        await commerce_case_api_client.get_commerce_case_request("merchantId", "")


@pytest.mark.asyncio
async def test_get_commerce_cases_request(commerce_case_api_client, mock_httpx_client):
    expected_response = [CommerceCaseResponse()]

    res = json.dumps([asdict(expected_response[0])])

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await commerce_case_api_client.get_commerce_cases_request("merchantId")
    assert response == expected_response


@pytest.mark.asyncio
async def test_get_commerce_cases_request_no_merchant_id_error(
    commerce_case_api_client,
):
    with pytest.raises(ValueError):
        await commerce_case_api_client.get_commerce_cases_request("")


@pytest.mark.asyncio
async def test_get_commerce_cases_request_with_query_params(
    commerce_case_api_client, mock_httpx_client
):
    expected_response = [CommerceCaseResponse()]

    res = json.dumps([asdict(expected_response[0])])

    mock_response = httpx.Response(200, text=res)

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = (
        mock_response
    )

    response = await commerce_case_api_client.get_commerce_cases_request(
        "merchantId", GetCommerceCasesQuery()
    )
    assert response == expected_response


@pytest.mark.asyncio
async def test_update_commerce_case_request(
    commerce_case_api_client, mock_httpx_client
):
    res = httpx.Response(200, text="")

    mock_httpx_client.return_value.__aenter__.return_value.request.return_value = res

    await commerce_case_api_client.update_commerce_case_request(
        "merchantId", "commerceCaseId", Customer()
    )


@pytest.mark.asyncio
async def test_update_commerce_case_request_no_merchant_id_error(
    commerce_case_api_client,
):
    with pytest.raises(ValueError):
        await commerce_case_api_client.update_commerce_case_request(
            "", "commerceCaseId", Customer()
        )


@pytest.mark.asyncio
async def test_update_commerce_case_request_no_commerce_case_id_error(
    commerce_case_api_client,
):
    with pytest.raises(ValueError):
        await commerce_case_api_client.update_commerce_case_request(
            "merchantId", "", Customer()
        )
