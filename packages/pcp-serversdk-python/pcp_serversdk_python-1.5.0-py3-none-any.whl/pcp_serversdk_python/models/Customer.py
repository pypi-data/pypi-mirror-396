from dataclasses import dataclass
from typing import Optional

from .Address import Address
from .BusinessRelation import BusinessRelation
from .CompanyInformation import CompanyInformation
from .ContactDetails import ContactDetails
from .CustomerAccount import CustomerAccount
from .PersonalInformation import PersonalInformation


@dataclass(kw_only=True)
class Customer:
    companyInformation: Optional[CompanyInformation] = None
    merchantCustomerId: Optional[str] = None
    billingAddress: Optional[Address] = None
    contactDetails: Optional[ContactDetails] = None
    fiscalNumber: Optional[str] = None
    businessRelation: Optional[BusinessRelation] = None
    locale: Optional[str] = None
    personalInformation: Optional[PersonalInformation] = None
    account: Optional[CustomerAccount] = None
