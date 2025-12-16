from urllib.parse import urljoin

import httpx

from ..models.AuthenticationToken import AuthenticationToken
from .BaseApiClient import BaseApiClient


class AuthenticationApiClient(BaseApiClient):
    async def get_authentication_tokens(
        self, merchant_id: str, request_id: str = None
    ) -> AuthenticationToken:
        if not merchant_id:
            raise ValueError(self.MERCHANT_ID_REQUIRED_ERROR)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/authentication-tokens",
        )
        headers = {"Content-Type": self.CONTENT_TYPE}
        if request_id:
            headers["X-Request-ID"] = request_id

        req = httpx.Request(
            "POST",
            url,
            headers=headers,
            content=b"{}",
        )
        return await self.make_api_call_with_type(req, AuthenticationToken)
