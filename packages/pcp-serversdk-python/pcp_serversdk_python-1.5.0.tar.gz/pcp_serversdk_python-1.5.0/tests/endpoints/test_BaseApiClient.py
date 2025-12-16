import httpx
import pytest

from pcp_serversdk_python.CommunicatorConfiguration import CommunicatorConfiguration
from pcp_serversdk_python.endpoints.BaseApiClient import BaseApiClient


@pytest.fixture
def communicator_configuration():
    return CommunicatorConfiguration("apiKey", "apiSecret", "https://test.com")


@pytest.fixture
def communicator_configuration_with_http_client():
    http_client = httpx.AsyncClient(timeout=30.0)
    return CommunicatorConfiguration(
        "apiKey", 
        "apiSecret", 
        "https://test.com", 
        http_client)


@pytest.fixture
def base_api_client(communicator_configuration):
    return BaseApiClient(communicator_configuration)


@pytest.fixture
def base_api_client_with_global_http_client(
    communicator_configuration_with_http_client,
):
    return BaseApiClient(communicator_configuration_with_http_client)


def test_base_api_client_initialization(base_api_client):
    """Test that BaseApiClient initializes correctly."""
    assert base_api_client.config is not None
    assert base_api_client.request_header_generator is not None
    assert base_api_client.http_client is None


def test_set_http_client(base_api_client):
    """Test setting a custom HTTP client on the API client."""
    custom_client = httpx.AsyncClient(timeout=60.0)
    
    # Initially None
    assert base_api_client.http_client is None
    
    # Set custom client
    base_api_client.set_http_client(custom_client)
    assert base_api_client.http_client == custom_client
    
    # Set to None
    base_api_client.set_http_client(None)
    assert base_api_client.http_client is None


def test_get_http_client_priority_client_specific(base_api_client):
    """Test that client-specific HTTP client has highest priority."""
    global_client = httpx.AsyncClient(timeout=30.0)
    client_specific_client = httpx.AsyncClient(timeout=60.0)
    
    # Set global client
    base_api_client.config.set_http_client(global_client)
    
    # Set client-specific client
    base_api_client.set_http_client(client_specific_client)
    
    # Client-specific should have priority
    assert base_api_client.get_http_client() == client_specific_client


def test_get_http_client_priority_global(base_api_client):
    """Test that global HTTP client is used when no client-specific client is set."""
    global_client = httpx.AsyncClient(timeout=30.0)
    
    # Set global client
    base_api_client.config.set_http_client(global_client)
    
    # No client-specific client set
    assert base_api_client.http_client is None
    
    # Global client should be returned
    assert base_api_client.get_http_client() == global_client


def test_get_http_client_priority_default(base_api_client):
    """Test that None is returned when no custom clients are configured."""
    # No global or client-specific client set
    assert base_api_client.config.get_http_client() is None
    assert base_api_client.http_client is None
    
    # Should return None (default)
    assert base_api_client.get_http_client() is None


def test_get_http_client_with_global_from_config(
    base_api_client_with_global_http_client,
):
    """Test that global HTTP client from configuration is used."""
    # Should return the global client from configuration
    global_client = base_api_client_with_global_http_client.config.get_http_client()
    assert base_api_client_with_global_http_client.get_http_client() == global_client


def test_get_http_client_client_specific_overrides_global(
    base_api_client_with_global_http_client,
):
    """Test that client-specific HTTP client overrides global configuration."""
    client_specific_client = httpx.AsyncClient(timeout=90.0)

    # Set client-specific client
    base_api_client_with_global_http_client.set_http_client(client_specific_client)

    # Client-specific should override global
    assert (
        base_api_client_with_global_http_client.get_http_client()
        == client_specific_client
    )

    # Global should still be available in config
    assert base_api_client_with_global_http_client.config.get_http_client() is not None
    assert (
        base_api_client_with_global_http_client.config.get_http_client()
        != client_specific_client
    )


@pytest.mark.asyncio
async def test_get_response_with_custom_client(base_api_client, mocker):
    """Test that get_response uses custom HTTP client when configured."""
    # Create a mock custom client
    mock_custom_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(200, text="test response")
    mock_custom_client.request.return_value = mock_response
    
    # Set custom client
    base_api_client.set_http_client(mock_custom_client)
    
    # Create a test request
    request = httpx.Request("GET", "https://test.com/api")
    
    # Call get_response
    response = await base_api_client.get_response(request)
    
    # Verify custom client was used
    mock_custom_client.request.assert_called_once_with(
        method="GET",
        url="https://test.com/api",
        headers=request.headers,
        content=request.content,
    )
    assert response == mock_response


@pytest.mark.asyncio
async def test_get_response_with_default_client(base_api_client, mocker):
    """Test that get_response creates default client when no 
    custom client is configured."""

    # Mock httpx.AsyncClient
    mock_client_instance = mocker.AsyncMock()
    mock_response = httpx.Response(200, text="test response")
    mock_client_instance.request.return_value = mock_response
    
    mock_async_client = mocker.patch("httpx.AsyncClient")
    mock_async_client.return_value.__aenter__.return_value = mock_client_instance
    
    # Create a test request
    request = httpx.Request("GET", "https://test.com/api")
    
    # Call get_response (no custom client set)
    response = await base_api_client.get_response(request)
    
    # Verify default client was created and used
    mock_async_client.assert_called_once()
    mock_client_instance.request.assert_called_once_with(
        method="GET",
        url="https://test.com/api",
        headers=request.headers,
        content=request.content,
    )
    assert response == mock_response
