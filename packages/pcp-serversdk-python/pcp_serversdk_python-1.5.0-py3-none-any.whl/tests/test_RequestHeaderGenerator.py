import base64
import json
from datetime import datetime, timezone

import httpx
import pytest

from pcp_serversdk_python.CommunicatorConfiguration import CommunicatorConfiguration
from pcp_serversdk_python.RequestHeaderGenerator import RequestHeaderGenerator
from pcp_serversdk_python.utils import ServerMetaInfo


@pytest.fixture
def communicator_configuration():
    TEST_API_KEY = "KEY"
    TEST_API_SECRET = "Super duper Ethan Hunt level secret"
    TEST_HOST = "awesome-api.com"
    return CommunicatorConfiguration(TEST_API_KEY, TEST_API_SECRET, TEST_HOST)


def test_constructs(communicator_configuration):
    request_header_generator = RequestHeaderGenerator(communicator_configuration)
    assert request_header_generator is not None


def test_signature_generation_for_get(communicator_configuration):
    request_header_generator = RequestHeaderGenerator(communicator_configuration)
    init = httpx.Request(
        url="http://awesome-api.com/v1/commerce_cases",
        method="GET",
        headers={
            "Date": datetime.fromtimestamp(1720520499, timezone.utc).strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            ),
            "X-GCS-ServerMetaInfo": "server fixed",
            "X-GCS-ClientMetaInfo": "client fixed",
        },
    )
    updated_request = request_header_generator.generate_additional_request_headers(
        init,
    )
    updated_headers = updated_request.headers
    auth_header = updated_headers.get("Authorization")
    assert auth_header == "GCS v1HMAC:KEY:ZSq7H19dyhyNGSPY5UgyPwITc5n4QG+zHnNDExIa6A8="


def test_signature_generation_with_content_type(communicator_configuration):
    request_header_generator = RequestHeaderGenerator(communicator_configuration)
    init = httpx.Request(
        url="http://awesome-api.com/v1/commerce_cases",
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Date": datetime.fromtimestamp(1720520499, timezone.utc).strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            ),
            "X-GCS-ServerMetaInfo": "server fixed",
            "X-GCS-ClientMetaInfo": "client fixed",
        },
    )
    updated_request = request_header_generator.generate_additional_request_headers(
        init,
    )
    updated_headers = updated_request.headers
    auth_header = updated_headers.get("Authorization")
    assert auth_header == "GCS v1HMAC:KEY:c5aNDw4AUxRChugRyN0OmTCs38YLA9E/tR+k0bOQzyk="


def test_add_a_date_header_if_missing(communicator_configuration):
    request_header_generator = RequestHeaderGenerator(communicator_configuration)
    init = httpx.Request(
        url="http://awesome-api.com/v1/commerce_cases", method="GET", headers={}
    )
    updated_request = request_header_generator.generate_additional_request_headers(
        init,
    )
    updated_headers = updated_request.headers
    date_header = updated_headers.get("Date")
    assert date_header is not None
    assert date_header != ""


def test_add_server_meta_info_if_missing(communicator_configuration):
    request_header_generator = RequestHeaderGenerator(communicator_configuration)
    init = httpx.Request(
        url="http://awesome-api.com/v1/commerce_cases", method="GET", headers={}
    )
    updated_request = request_header_generator.generate_additional_request_headers(
        init,
    )
    updated_headers = updated_request.headers
    print(updated_headers)
    server_meta_info_header_base64 = updated_headers.get("X-GCS-ServerMetaInfo")
    meta = ServerMetaInfo()
    json_string = json.dumps(meta.__dict__)
    expected_as_base64 = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
    assert server_meta_info_header_base64 == expected_as_base64


def test_add_server_client_info_if_missing(communicator_configuration):
    request_header_generator = RequestHeaderGenerator(communicator_configuration)
    init = httpx.Request(
        url="http://awesome-api.com/v1/commerce_cases", method="GET", headers={}
    )
    updated_request = request_header_generator.generate_additional_request_headers(
        init,
    )
    updated_headers = updated_request.headers
    client_meta_info_header_base64 = updated_headers.get("X-GCS-ClientMetaInfo")
    json_string = '"[]"'
    expected_as_base64 = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
    assert client_meta_info_header_base64 == expected_as_base64
