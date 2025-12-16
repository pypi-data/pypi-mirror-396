import json
from dataclasses import asdict
from typing import Optional
from urllib.parse import urljoin

import httpx

from ..models import (
    CheckoutResponse,
    CheckoutsResponse,
    CompleteOrderRequest,
    CompletePaymentResponse,
    CreateCheckoutRequest,
    CreateCheckoutResponse,
    PatchCheckoutRequest,
)
from ..queries import GetCheckoutsQuery
from .BaseApiClient import (
    BaseApiClient,
)


class CheckoutApiClient(BaseApiClient):
    async def create_checkout_request(
        self, merchant_id: str, commerce_case_id: str, payload: CreateCheckoutRequest
    ) -> CreateCheckoutResponse:
        self._validate_inputs(merchant_id, commerce_case_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, CreateCheckoutResponse)

    async def get_checkout_request(
        self, merchant_id: str, commerce_case_id: str, checkout_id: str
    ) -> CheckoutResponse:
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}",
        )

        req = httpx.Request("GET", url, headers={})

        return await self.make_api_call_with_type(req, CheckoutResponse)

    async def get_checkouts_request(
        self, merchant_id: str, query_params: Optional[GetCheckoutsQuery] = None
    ) -> CheckoutsResponse:
        self._validate_inputs(merchant_id)

        url = urljoin(self.get_config().get_host(), f"/v1/{merchant_id}/checkouts")

        if query_params:
            query_string = query_params.to_query_map()
            url = f"{url}?{query_string}"

        req = httpx.Request("GET", url, headers={})

        return await self.make_api_call_with_type(req, CheckoutsResponse)

    async def update_checkout_request(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payload: PatchCheckoutRequest,
    ) -> None:
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}",
        )

        req = httpx.Request(
            "PATCH",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        await self.make_api_call(req)

    async def remove_checkout_request(
        self, merchant_id: str, commerce_case_id: str, checkout_id: str
    ) -> None:
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}",
        )

        req = httpx.Request(
            "DELETE",
            url,
            headers={},
        )

        await self.make_api_call(req)

    def _validate_inputs(
        self, merchant_id: str, commerce_case_id: str = None, checkout_id: str = None
    ):
        if not merchant_id:
            raise ValueError(self.MERCHANT_ID_REQUIRED_ERROR)
        if commerce_case_id is not None and not commerce_case_id:
            raise ValueError(self.COMMERCE_CASE_ID_REQUIRED_ERROR)
        if checkout_id is not None and not checkout_id:
            raise ValueError(self.CHECKOUT_ID_REQUIRED_ERROR)

    async def complete_checkout_request(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payload: CompleteOrderRequest,
    ) -> CompletePaymentResponse:
        """Complete a checkout request with order details."""
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/complete-order",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, CompletePaymentResponse)
