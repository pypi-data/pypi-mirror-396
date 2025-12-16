import json
from dataclasses import asdict
from typing import Optional
from urllib.parse import urljoin

import httpx

from ..models import (
    CommerceCaseResponse,
    CreateCommerceCaseRequest,
    CreateCommerceCaseResponse,
    Customer,
)
from ..queries import GetCommerceCasesQuery
from .BaseApiClient import (
    BaseApiClient,
)


class CommerceCaseApiClient(BaseApiClient):
    async def create_commerce_case_request(
        self, merchant_id: str, payload: CreateCommerceCaseRequest
    ) -> CreateCommerceCaseResponse:
        self._validate_inputs(merchant_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, CreateCommerceCaseResponse)

    async def get_commerce_case_request(
        self, merchant_id: str, commerce_case_id: str
    ) -> CommerceCaseResponse:
        self._validate_inputs(merchant_id, commerce_case_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}",
        )

        req = httpx.Request("GET", url, headers={})

        return await self.make_api_call_with_type(req, CommerceCaseResponse)

    async def get_commerce_cases_request(
        self, merchant_id: str, query_params: Optional[GetCommerceCasesQuery] = None
    ) -> list[CommerceCaseResponse]:
        self._validate_inputs(merchant_id)

        url = urljoin(self.get_config().get_host(), f"/v1/{merchant_id}/commerce-cases")

        if query_params:
            query_string = query_params.to_query_map()
            url = f"{url}?{query_string}"

        req = httpx.Request("GET", url, headers={})

        return await self.make_api_call_with_type(req, list[CommerceCaseResponse])

    async def update_commerce_case_request(
        self, merchant_id: str, commerce_case_id: str, payload: Customer
    ):
        self._validate_inputs(merchant_id, commerce_case_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}",
        )

        req = httpx.Request(
            "PATCH",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps({"customer": asdict(payload)}),
        )

        return await self.make_api_call(req)

    def _validate_inputs(
        self,
        merchant_id: str,
        commerce_case_id: str = None,
    ):
        if not merchant_id:
            raise ValueError(self.MERCHANT_ID_REQUIRED_ERROR)
        # Check the commerce_case_id only if it is provided
        if commerce_case_id is not None and not commerce_case_id:
            raise ValueError(self.COMMERCE_CASE_ID_REQUIRED_ERROR)
