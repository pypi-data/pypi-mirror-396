from pcp_serversdk_python.errors import ApiErrorResponseException
from pcp_serversdk_python.models import APIError


def test_api_error_response_exception_initialization():
    status_code = 404
    response_body = "Not Found"
    errors = [APIError(id="error_id", errorCode="error_message")]

    exception = ApiErrorResponseException(
        status_code=status_code, response_body=response_body, errors=errors
    )

    # Check initialization
    assert exception.status_code == status_code
    assert exception.response_body == response_body
    assert exception.errors == errors


def test_api_error_response_exception_initialization_with_defaults():
    status_code = 404
    response_body = "Not Found"

    exception = ApiErrorResponseException(
        status_code=status_code, response_body=response_body
    )

    # Check initialization with default values
    assert exception.status_code == status_code
    assert exception.response_body == response_body
    assert exception.errors == []


def test_get_errors():
    errors = [APIError(id="error_id", errorCode="error_message")]
    exception = ApiErrorResponseException(
        status_code=404, response_body="Not Found", errors=errors
    )

    # Check get_errors method
    assert exception.get_errors() == errors
