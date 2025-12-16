from dataclasses import dataclass, field
from typing import Optional


@dataclass(kw_only=True)
class ApplePayPaymentContact:
    phoneNumber: Optional[str] = None
    emailAddress: Optional[str] = None
    givenName: Optional[str] = None
    familyName: Optional[str] = None
    phoneticGivenName: Optional[str] = None
    phoneticFamilyName: Optional[str] = None
    addressLines: Optional[list[str]] = field(default_factory=list)
    locality: Optional[str] = None
    postalCode: Optional[str] = None
    administrativeArea: Optional[str] = None
    subAdministrativeArea: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
