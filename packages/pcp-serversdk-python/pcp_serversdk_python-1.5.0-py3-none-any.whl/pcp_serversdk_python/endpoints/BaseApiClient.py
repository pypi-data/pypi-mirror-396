import json
from enum import Enum
from typing import (
    Any,
    Optional,
    TypeVar,
    get_args,
    get_origin,
)

import httpx
from dacite import Config, from_dict

from ..CommunicatorConfiguration import CommunicatorConfiguration
from ..errors import (
    ApiErrorResponseException,
    ApiResponseRetrievalException,
)
from ..models import ErrorResponse
from ..RequestHeaderGenerator import RequestHeaderGenerator

T = TypeVar("T")


def from_dict_with_enum(
    data_class: type[T],
    data: dict[str, Any],
) -> T:
    return from_dict(data_class=data_class, data=data, config=Config(cast=[Enum]))


def is_error_response(parsed: Any) -> bool:
    if not isinstance(parsed, dict):
        return False
    if "errorId" in parsed and not isinstance(parsed["errorId"], str):
        return False
    if "errors" in parsed and not isinstance(parsed["errors"], list):  # noqa: SIM103
        return False
    return True


class BaseApiClient:
    CONTENT_TYPE = "application/json"
    MERCHANT_ID_REQUIRED_ERROR = "Merchant ID is required"
    COMMERCE_CASE_ID_REQUIRED_ERROR = "Commerce Case ID is required"
    CHECKOUT_ID_REQUIRED_ERROR = "Checkout ID is required"
    PAYMENT_INFORMATION_ID_REQUIRED_ERROR = "Payment Information ID is required"
    PAYMENT_EXECUTION_ID_REQUIRED_ERROR = "Payment Execution ID is required"
    JSON_PARSE_ERROR = "Failed to parse JSON response"

    def __init__(self, config: CommunicatorConfiguration):
        self.config = config
        self.request_header_generator = RequestHeaderGenerator(config)
        self.http_client: Optional[httpx.AsyncClient] = None

    def get_request_header_generator(self) -> Optional[RequestHeaderGenerator]:
        return self.request_header_generator

    def get_config(self) -> CommunicatorConfiguration:
        return self.config

    def set_http_client(self, http_client: Optional[httpx.AsyncClient]) -> None:
        """Set a custom HTTP client for this API client instance.

        Args:
            http_client: The custom httpx.AsyncClient to use for requests.
                        If None, will fall back to global or default client.
        """
        self.http_client = http_client

    def get_http_client(self) -> Optional[httpx.AsyncClient]:
        """Get the HTTP client to use for requests, following priority logic.

        Priority order:
        1. Client-specific HTTP client (set via set_http_client)
        2. Global HTTP client (from CommunicatorConfiguration)
        3. None (will create default client)

        Returns:
            The HTTP client to use, or None if default should be created.
        """
        # Priority 1: Client-specific HTTP client
        if self.http_client is not None:
            return self.http_client

        # Priority 2: Global HTTP client from configuration
        if self.config.get_http_client() is not None:
            return self.config.get_http_client()

        # Priority 3: None (default client will be created)
        return None

    async def make_api_call(self, request: httpx.Request) -> None:
        if self.request_header_generator:
            request = self.request_header_generator.generate_additional_request_headers(
                request
            )
        response = await self.get_response(request)

        await self.handle_error(response)

    async def make_api_call_with_type(self, request: httpx.Request, type: type[T]) -> T:
        if self.request_header_generator:
            request = self.request_header_generator.generate_additional_request_headers(
                request
            )
        response = await self.get_response(request)
        await self.handle_error(response)
        try:
            data = json.loads(response.text)
            # Check if the expected type is a List
            if get_origin(type) is list:
                item_type = get_args(type)[0]  # Extract the type of the list's elements
                return [
                    from_dict_with_enum(data_class=item_type, data=item)
                    for item in data
                ]
            else:
                return from_dict_with_enum(data_class=type, data=data)
        except json.JSONDecodeError as e:
            raise AssertionError(self.JSON_PARSE_ERROR) from e

    async def handle_error(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        response_body = response.text
        if not response_body:
            raise ApiResponseRetrievalException(response.status_code, response_body)
        try:
            data = json.loads(response.text)
            error = from_dict_with_enum(data_class=ErrorResponse, data=data)
            raise ApiErrorResponseException(
                response.status_code, response_body, error.errors
            )
        except json.JSONDecodeError as e:
            raise ApiResponseRetrievalException(response.status_code, response_body, e)  # noqa: B904

    async def get_response(self, request: httpx.Request) -> httpx.Response:
        # Get the HTTP client to use based on priority logic
        configured_client = self.get_http_client()

        if configured_client is not None:
            # Use the configured client (either client-specific or global)
            response = await configured_client.request(
                method=request.method,
                url=str(request.url),
                headers=request.headers,
                content=request.content,
            )
        else:
            # Fall back to creating a default client
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=str(request.url),
                    headers=request.headers,
                    content=request.content,
                )

        return response
