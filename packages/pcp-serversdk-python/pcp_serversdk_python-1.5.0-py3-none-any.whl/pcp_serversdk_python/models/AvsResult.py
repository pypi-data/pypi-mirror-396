from enum import Enum


class AvsResult(Enum):
    """Result of the Address Verification Service checks."""

    A = "A"  # Address (Street) matches, Zip does not
    B = "B"  # Street address match for international transactions—Postal code not verified
    C = "C"  # Street address and postal code not verified for international transaction
    D = "D"  # Street address and postal code match for international transaction, cardholder name is incorrect
    E = "E"  # AVS error
    F = "F"  # Address does match and five digit ZIP code does match (UK only)
    G = "G"  # Address information is unavailable; international transaction; non-AVS participant
    H = "H"  # Billing address and postal code match, cardholder name is incorrect (Amex)
    I_CODE = "I"  # Address information not verified for international transaction
    K = "K"  # Cardholder name matches (Amex)
    L = "L"  # Cardholder name and postal code match (Amex)
    M = "M"  # Cardholder name, street address, and postal code match for international transaction
    N = "N"  # No Match on Address (Street) or Zip
    O_CODE = "O"  # Cardholder name and address match (Amex)
    P = "P"  # Postal codes match for international transaction—Street address not verified
    Q = "Q"  # Billing address matches, cardholder is incorrect (Amex)
    R = "R"  # Retry, System unavailable or Timed out
    S = "S"  # Service not supported by issuer
    U = "U"  # Address information is unavailable
    W = "W"  # 9 digit Zip matches, Address (Street) does not
    X = "X"  # Exact AVS Match
    Y = "Y"  # Address (Street) and 5 digit Zip match
    Z = "Z"  # 5 digit Zip matches, Address (Street) does not
    ZERO = "0"  # No service available
