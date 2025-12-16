import json
from dataclasses import asdict
from urllib.parse import urljoin

import httpx

from ..models import (
    PaymentInformationRefundRequest,
    PaymentInformationRefundResponse,
    PaymentInformationRequest,
    PaymentInformationResponse,
)
from .BaseApiClient import (
    BaseApiClient,
)


class PaymentInformationApiClient(BaseApiClient):
    async def create_payment_information(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payload: PaymentInformationRequest,
    ):
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-information",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, PaymentInformationResponse)

    async def get_payment_information(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_information_id: str,
    ):
        self._validate_inputs(
            merchant_id, commerce_case_id, checkout_id, payment_information_id
        )

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-information/{payment_information_id}",
        )

        req = httpx.Request("GET", url)

        return await self.make_api_call_with_type(req, PaymentInformationResponse)

    def _validate_inputs(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_information_id: str = None,
    ):
        if not merchant_id:
            raise ValueError(self.MERCHANT_ID_REQUIRED_ERROR)
        if not commerce_case_id:
            raise ValueError(self.COMMERCE_CASE_ID_REQUIRED_ERROR)
        if not checkout_id:
            raise ValueError(self.CHECKOUT_ID_REQUIRED_ERROR)
        # Check the payment_information_id only if it is provided
        if payment_information_id is not None and not payment_information_id:
            raise ValueError(self.PAYMENT_INFORMATION_ID_REQUIRED_ERROR)

    async def refund_payment_information(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_information_id: str,
        payload: PaymentInformationRefundRequest,
    ) -> PaymentInformationRefundResponse:
        """Refund a payment information."""
        self._validate_inputs(
            merchant_id, commerce_case_id, checkout_id, payment_information_id
        )

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-information/{payment_information_id}/refund",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, PaymentInformationRefundResponse)
