from enum import Enum


class ActionType(Enum):
    """Action merchants needs to take in the online payment process."""

    REDIRECT = "REDIRECT"  # The customer needs to be redirected using the details found in redirectData
    SHOW_FORM = "SHOW_FORM"  # The customer needs to be shown a form with the fields found in formFields
    SHOW_INSTRUCTIONS = "SHOW_INSTRUCTIONS"  # The customer needs to be shown payment instruction using the details found in showData
    SHOW_TRANSACTION_RESULTS = "SHOW_TRANSACTION_RESULTS"  # The customer needs to be shown the transaction results using the details found in showData
    MOBILE_THREEDS_CHALLENGE = "MOBILE_THREEDS_CHALLENGE"  # The customer needs to complete a challenge as part of the 3D Secure authentication inside your mobile app
    CALL_THIRD_PARTY = "CALL_THIRD_PARTY"  # The merchant needs to call a third party using the data found in thirdPartyData
