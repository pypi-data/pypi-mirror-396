import pytest

from pcp_serversdk_python.models import (
    ApplePaymentDataTokenHeaderInformation,
    ApplePaymentDataTokenInformation,
    ApplePaymentTokenVersion,
    ApplePayPayment,
    MobilePaymentMethodSpecificInput,
    Network,
    PaymentProduct302SpecificInput,
)
from pcp_serversdk_python.transformer.ApplepayTransformer import (
    network_from_string,
    transform_apple_pay_payment_to_mobile_payment_method_specific_input,
    version_from_string,
)


def test_network_from_string():
    assert network_from_string("mastercard") == Network.MASTERCARD
    assert network_from_string("VISA") == Network.VISA
    assert network_from_string("AmEx") == Network.AMEX
    assert network_from_string("GIROCARD") == Network.GIROCARD
    assert network_from_string("discover") == Network.DISCOVER
    assert network_from_string("JCB") == Network.JCB
    with pytest.raises(TypeError):
        network_from_string("UNKNOWN")


def test_version_from_string():
    assert version_from_string("EC_V1") == ApplePaymentTokenVersion.EC_V1
    with pytest.raises(TypeError):
        version_from_string("UNKNOWN")


def test_transform_apple_pay_payment_to_mobile_payment_method_specific_input():
    payment = ApplePayPayment(
        token={
            "paymentData": {
                "header": {
                    "publicKeyHash": "publicKeyHash123",
                    "ephemeralPublicKey": "ephemeralPublicKey123",
                    "transactionId": "transactionId123",
                    "applicationData": "applicationData123",
                },
                "version": "EC_V1",
                "signature": "signature123",
            },
            "paymentMethod": {
                "network": "VISA",
            },
        }
    )

    expected_output = MobilePaymentMethodSpecificInput(
        paymentProductId=302,
        publicKeyHash="publicKeyHash123",
        ephemeralKey="ephemeralPublicKey123",
        paymentProduct302SpecificInput=PaymentProduct302SpecificInput(
            network=Network.VISA,
            token=ApplePaymentDataTokenInformation(
                version=ApplePaymentTokenVersion.EC_V1,
                signature="signature123",
                header=ApplePaymentDataTokenHeaderInformation(
                    transactionId="transactionId123",
                    applicationData="applicationData123",
                ),
            ),
        ),
    )

    result = transform_apple_pay_payment_to_mobile_payment_method_specific_input(
        payment
    )

    assert result == expected_output
