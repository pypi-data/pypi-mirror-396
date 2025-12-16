from ..models import APIError
from .ApiException import ApiException


class ApiErrorResponseException(ApiException):
    def __init__(
        self, status_code: int, response_body: str, errors: list[APIError] = None
    ):
        super().__init__(status_code, response_body)
        self.errors = errors if errors else []

    def get_errors(self) -> list[APIError]:
        return self.errors
