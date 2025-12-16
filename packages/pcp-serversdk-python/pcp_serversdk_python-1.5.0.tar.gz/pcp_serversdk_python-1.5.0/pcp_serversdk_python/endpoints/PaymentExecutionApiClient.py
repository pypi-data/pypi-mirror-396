import json
from dataclasses import asdict
from urllib.parse import urljoin

import httpx

from ..models import (
    CancelPaymentRequest,
    CancelPaymentResponse,
    CapturePaymentRequest,
    CapturePaymentResponse,
    CompletePaymentRequest,
    CompletePaymentResponse,
    CreatePaymentResponse,
    PausePaymentRequest,
    PausePaymentResponse,
    PaymentExecution,
    PaymentExecutionRequest,
    RefreshPaymentRequest,
    RefundPaymentResponse,
    RefundRequest,
)
from .BaseApiClient import BaseApiClient


class PaymentExecutionApiClient(BaseApiClient):
    async def create_payment(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payload: PaymentExecutionRequest,
    ):
        self._validate_inputs(merchant_id, commerce_case_id, checkout_id)

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-executions",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, CreatePaymentResponse)

    async def capture_payment(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_execution_id: str,
        payload: CapturePaymentRequest,
    ):
        self._validate_inputs(
            merchant_id, commerce_case_id, checkout_id, payment_execution_id
        )

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-executions/{payment_execution_id}/capture",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, CapturePaymentResponse)

    async def cancel_payment(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_execution_id: str,
        payload: CancelPaymentRequest,
    ):
        self._validate_inputs(
            merchant_id, commerce_case_id, checkout_id, payment_execution_id
        )

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-executions/{payment_execution_id}/cancel",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, CancelPaymentResponse)

    async def refund_payment(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_execution_id: str,
        payload: RefundRequest,
    ):
        self._validate_inputs(
            merchant_id, commerce_case_id, checkout_id, payment_execution_id
        )

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-executions/{payment_execution_id}/refund",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, RefundPaymentResponse)

    async def complete_payment(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_execution_id: str,
        payload: CompletePaymentRequest,
    ):
        self._validate_inputs(
            merchant_id, commerce_case_id, checkout_id, payment_execution_id
        )

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-executions/{payment_execution_id}/complete",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, CompletePaymentResponse)

    def _validate_inputs(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_execution_id: str = None,
    ):
        if not merchant_id:
            raise ValueError(self.MERCHANT_ID_REQUIRED_ERROR)
        if not commerce_case_id:
            raise ValueError(self.COMMERCE_CASE_ID_REQUIRED_ERROR)
        if not checkout_id:
            raise ValueError(self.CHECKOUT_ID_REQUIRED_ERROR)
        # Check the payment_execution_id only if it is provided
        if payment_execution_id is not None and not payment_execution_id:
            raise ValueError(self.PAYMENT_EXECUTION_ID_REQUIRED_ERROR)

    async def pause_payment(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_execution_id: str,
        payload: PausePaymentRequest,
    ) -> PausePaymentResponse:
        """Pause a payment execution."""
        self._validate_inputs(
            merchant_id, commerce_case_id, checkout_id, payment_execution_id
        )

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-executions/{payment_execution_id}/pause",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, PausePaymentResponse)

    async def refresh_payment(
        self,
        merchant_id: str,
        commerce_case_id: str,
        checkout_id: str,
        payment_execution_id: str,
        payload: RefreshPaymentRequest,
    ) -> PaymentExecution:
        """Refresh a payment execution."""
        self._validate_inputs(
            merchant_id, commerce_case_id, checkout_id, payment_execution_id
        )

        url = urljoin(
            self.get_config().get_host(),
            f"/v1/{merchant_id}/commerce-cases/{commerce_case_id}/checkouts/{checkout_id}/payment-executions/{payment_execution_id}/refresh",
        )

        req = httpx.Request(
            "POST",
            url,
            headers={"Content-Type": self.CONTENT_TYPE},
            data=json.dumps(asdict(payload)),
        )

        return await self.make_api_call_with_type(req, PaymentExecution)
