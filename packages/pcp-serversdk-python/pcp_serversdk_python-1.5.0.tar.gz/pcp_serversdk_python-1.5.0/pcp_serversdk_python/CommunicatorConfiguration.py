from typing import Optional

import httpx


class CommunicatorConfiguration:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        host: str,
        http_client: Optional[httpx.AsyncClient] = None
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.host = host
        self.http_client = http_client

    def get_api_key(self) -> str:
        return self.api_key

    def get_api_secret(self) -> str:
        return self.api_secret

    def get_host(self) -> str:
        return self.host

    def get_http_client(self) -> Optional[httpx.AsyncClient]:
        return self.http_client

    def set_http_client(self, http_client: Optional[httpx.AsyncClient]) -> None:
        self.http_client = http_client
