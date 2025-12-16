from enum import Enum


class AuthorizationMode(str, Enum):
    PRE_AUTHORIZATION = "PRE_AUTHORIZATION"
    SALE = "SALE"
