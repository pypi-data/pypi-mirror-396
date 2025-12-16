import httpx

from pcp_serversdk_python.CommunicatorConfiguration import (
    CommunicatorConfiguration,
)  # Update import as needed


def test_communicator_configuration_initialization():
    api_key = "testApiKey"
    api_secret = "testApiSecret"
    host = "https://example.com"

    config = CommunicatorConfiguration(
        api_key=api_key, api_secret=api_secret, host=host
    )

    # Check initialization
    assert config.api_key == api_key
    assert config.api_secret == api_secret
    assert config.host == host


def test_get_api_key():
    api_key = "testApiKey"
    config = CommunicatorConfiguration(
        api_key=api_key, api_secret="testApiSecret", host="https://example.com"
    )

    # Check get_api_key method
    assert config.get_api_key() == api_key


def test_get_api_secret():
    api_secret = "testApiSecret"
    config = CommunicatorConfiguration(
        api_key="testApiKey", api_secret=api_secret, host="https://example.com"
    )

    # Check get_api_secret method
    assert config.get_api_secret() == api_secret


def test_get_host():
    host = "https://example.com"
    config = CommunicatorConfiguration(
        api_key="testApiKey", api_secret="testApiSecret", host=host
    )

    # Check get_host method
    assert config.get_host() == host


def test_communicator_configuration_with_http_client():
    api_key = "testApiKey"
    api_secret = "testApiSecret"
    host = "https://example.com"
    http_client = httpx.AsyncClient(timeout=30.0)

    config = CommunicatorConfiguration(
        api_key=api_key, api_secret=api_secret, host=host, http_client=http_client
    )

    # Check initialization with HTTP client
    assert config.api_key == api_key
    assert config.api_secret == api_secret
    assert config.host == host
    assert config.http_client == http_client


def test_get_http_client():
    http_client = httpx.AsyncClient(timeout=30.0)
    config = CommunicatorConfiguration(
        api_key="testApiKey",
        api_secret="testApiSecret",
        host="https://example.com",
        http_client=http_client
    )

    # Check get_http_client method
    assert config.get_http_client() == http_client


def test_get_http_client_none():
    config = CommunicatorConfiguration(
        api_key="testApiKey", api_secret="testApiSecret", host="https://example.com"
    )

    # Check get_http_client method returns None when not set
    assert config.get_http_client() is None


def test_set_http_client():
    config = CommunicatorConfiguration(
        api_key="testApiKey", api_secret="testApiSecret", host="https://example.com"
    )

    # Initially None
    assert config.get_http_client() is None

    # Set HTTP client
    http_client = httpx.AsyncClient(timeout=30.0)
    config.set_http_client(http_client)

    # Check that it was set
    assert config.get_http_client() == http_client

    # Set to None
    config.set_http_client(None)
    assert config.get_http_client() is None
