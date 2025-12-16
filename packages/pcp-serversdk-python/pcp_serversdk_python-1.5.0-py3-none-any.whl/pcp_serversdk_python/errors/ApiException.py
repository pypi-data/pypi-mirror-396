class ApiException(Exception):
    def __init__(self, status_code: int, response_body: str):
        super().__init__(f"Status code: {status_code}, Response body: {response_body}")
        self.status_code = status_code
        self.response_body = response_body
