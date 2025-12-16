import json
from dataclasses import asdict
from urllib.parse import urljoin

import httpx

from ..models import (
    CancelRequest,
    CancelResponse,
    DeliverRequest,
    DeliverResponse,
    OrderRequest,
    OrderResponse,
    ReturnRequest,
    ReturnResponse,
)
from .BaseApiClient import (
    BaseApiClient,
)


class OrderManagementCheckoutActionsApiClient(BaseApiClient):
    async def create_order(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payload: OrderRequest,
    ) -> OrderResponse:
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/order",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, OrderResponse)

    async def deliver_order(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payload: DeliverRequest,
    ) -> DeliverResponse:
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/deliver",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, DeliverResponse)

    async def return_order(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payload: ReturnRequest,
    ) -> ReturnResponse:
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/return",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, ReturnResponse)

    async def cancel_order(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payload: CancelRequest,
    ) -> CancelResponse:
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/cancel",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, CancelResponse)

    def _validate_inputs(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
    ):
        if not merchant_id:
            raise ValueError(self.MERCHANT_ID_REQUIRED_ERROR)
        if not commerce_case_id:
            raise ValueError(self.COMMERCE_CASE_ID_REQUIRED_ERROR)
        if not checkout_id:
            raise ValueError(self.CHECKOUT_ID_REQUIRED_ERROR)
