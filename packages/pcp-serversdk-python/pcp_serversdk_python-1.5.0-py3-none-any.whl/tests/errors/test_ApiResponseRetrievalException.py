from pcp_serversdk_python.errors.ApiException import ApiException
from pcp_serversdk_python.errors.ApiResponseRetrievalException import (
    ApiResponseRetrievalException,
)


def test_api_response_retrieval_exception_initialization():
    status_code = 500
    response_body = "Internal Server Error"

    exception = ApiResponseRetrievalException(
        status_code=status_code, response_body=response_body
    )

    # Check initialization
    assert exception.status_code == status_code
    assert exception.response_body == response_body


def test_api_response_retrieval_exception_inheritance():
    status_code = 500
    response_body = "Internal Server Error"

    exception = ApiResponseRetrievalException(
        status_code=status_code, response_body=response_body
    )

    # Check inheritance
    assert isinstance(exception, ApiException)
    assert exception.status_code == status_code
    assert exception.response_body == response_body
