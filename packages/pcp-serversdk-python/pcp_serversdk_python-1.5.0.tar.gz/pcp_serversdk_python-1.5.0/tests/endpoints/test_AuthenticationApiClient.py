import pytest

from pcp_serversdk_python.CommunicatorConfiguration import CommunicatorConfiguration
from pcp_serversdk_python.endpoints import AuthenticationApiClient
from pcp_serversdk_python.models.AuthenticationToken import AuthenticationToken


@pytest.fixture
def authentication_api_client():
    config = CommunicatorConfiguration("apiKey", "apiSecret", "https://test.com")
    return AuthenticationApiClient(config)


@pytest.mark.asyncio
async def test_get_authentication_tokens_success(authentication_api_client, mocker):
    merchant_id = "test_merchant"
    expected_token = AuthenticationToken(
        token="abc",
        id="1",
        creationDate=None,
        expirationDate=None,
    )
    mocker.patch.object(
        authentication_api_client,
        "make_api_call_with_type",
        return_value=expected_token,
    )
    result = await authentication_api_client.get_authentication_tokens(merchant_id)
    assert isinstance(result, AuthenticationToken)
    assert result.token == "abc"
    assert result.id == "1"


@pytest.mark.asyncio
async def test_get_authentication_tokens_missing_merchant_id(authentication_api_client):
    with pytest.raises(ValueError) as exc:
        await authentication_api_client.get_authentication_tokens("")
    assert "Merchant ID is required" in str(exc.value)


@pytest.mark.asyncio
async def test_get_authentication_tokens_with_request_id_header(
    authentication_api_client, mocker
):
    merchant_id = "test_merchant"
    request_id = "req-123"
    expected_token = AuthenticationToken(
        token="abc",
        id="1",
        creationDate=None,
        expirationDate=None,
    )
    # Patch make_api_call_with_type to just return the expected token
    mocker.patch.object(
        authentication_api_client,
        "make_api_call_with_type",
        return_value=expected_token,
    )
    # Patch httpx.Request to capture headers
    original_request = authentication_api_client.get_authentication_tokens.__globals__[
        "httpx"
    ].Request
    captured = {}

    def fake_request(method, url, headers=None, content=None):
        captured["headers"] = headers
        return original_request(method, url, headers=headers, content=content)

    mocker.patch(
        "pcp_serversdk_python.endpoints.AuthenticationApiClient.httpx.Request",
        side_effect=fake_request,
        autospec=True,
    )
    await authentication_api_client.get_authentication_tokens(
        merchant_id, request_id=request_id
    )
    assert "X-Request-ID" in captured["headers"]
    assert captured["headers"]["X-Request-ID"] == request_id
