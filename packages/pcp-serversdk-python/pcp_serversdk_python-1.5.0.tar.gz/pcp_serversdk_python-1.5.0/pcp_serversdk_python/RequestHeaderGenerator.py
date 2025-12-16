import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

import httpx

from .CommunicatorConfiguration import CommunicatorConfiguration
from .utils.ServerMetaInfo import ServerMetaInfo


class RequestHeaderGenerator:
    SERVER_META_INFO_HEADER_NAME = "X-GCS-ServerMetaInfo"
    CLIENT_META_INFO_HEADER_NAME = "X-GCS-ClientMetaInfo"
    AUTHORIZATION_HEADER_NAME = "Authorization"
    DATE_HEADER_NAME = "Date"
    CONTENT_TYPE_HEADER_NAME = "Content-Type"
    ALGORITHM = "sha256"
    WHITESPACE_REGEX = r"\r?\n[h]*"

    def __init__(self, config: CommunicatorConfiguration):
        self.config = config

    def generate_additional_request_headers(
        self, request: httpx.Request
    ) -> httpx.Request:
        headers = request.headers.copy()
        if self.DATE_HEADER_NAME not in headers:
            headers[self.DATE_HEADER_NAME] = datetime.now(timezone.utc).strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )
        if self.SERVER_META_INFO_HEADER_NAME not in headers:
            headers[self.SERVER_META_INFO_HEADER_NAME] = self.get_server_meta_info()
        if self.CLIENT_META_INFO_HEADER_NAME not in headers:
            headers[self.CLIENT_META_INFO_HEADER_NAME] = self.get_client_meta_info()
        if self.AUTHORIZATION_HEADER_NAME not in headers:
            headers[self.AUTHORIZATION_HEADER_NAME] = self.get_auth_header(
                request, headers
            )

        request.headers = headers
        return request

    def get_auth_header(self, request: httpx.Request, headers: dict) -> str:
        string_to_sign = f"{request.method}\n"

        if self.CONTENT_TYPE_HEADER_NAME in headers:
            string_to_sign += f"{headers[self.CONTENT_TYPE_HEADER_NAME]}"
        string_to_sign += "\n"

        string_to_sign += f"{headers[self.DATE_HEADER_NAME]}\n"

        if self.CLIENT_META_INFO_HEADER_NAME in headers:
            string_to_sign += f"{self.CLIENT_META_INFO_HEADER_NAME.lower()}:{headers[self.CLIENT_META_INFO_HEADER_NAME]}\n"  # noqa: E501
        if self.SERVER_META_INFO_HEADER_NAME in headers:
            string_to_sign += f"{self.SERVER_META_INFO_HEADER_NAME.lower()}:{headers[self.SERVER_META_INFO_HEADER_NAME]}\n"  # noqa: E501

        url_internal = urlparse(request.url.__str__())
        string_to_sign += url_internal.path
        if url_internal.query:
            string_to_sign += f"{quote(url_internal.query)}"
        string_to_sign += "\n"
        signature = self.sign(string_to_sign)
        return f"GCS v1HMAC:{self.config.get_api_key()}:{signature}"

    def sign(self, target: str) -> str:
        hmac_instance = hmac.new(
            self.config.get_api_secret().encode(), target.encode(), hashlib.sha256
        )
        return base64.b64encode(hmac_instance.digest()).decode()

    def get_server_meta_info(self) -> str:
        meta = ServerMetaInfo()
        json_string = json.dumps(
            meta.__dict__
        )  # Assuming ServerMetaInfo has a dictionary representation
        return base64.b64encode(json_string.encode("utf-8")).decode("utf-8")

    def get_client_meta_info(self) -> str:
        encoded_bytes = base64.b64encode(b'"[]"')
        return encoded_bytes.decode("utf-8")
