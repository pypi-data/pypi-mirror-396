from dataclasses import dataclass
from typing import Optional

from .ProductType import ProductType


@dataclass(kw_only=True)
class OrderLineDetailsInput:
    """Object containing additional information that when supplied can have a
    beneficial effect on the discount rates."""

    productPrice: int
    """The price of one unit of the product, the value should be zero or greater.
    @minimum 0
    @maximum 2147483647"""

    quantity: int
    """Quantity of the units being purchased, should be greater than zero.
    Note: Must not be all spaces or all zeros.
    @minimum 0
    @maximum 9999"""

    productCode: Optional[str] = None
    """Product or UPC Code."""

    productType: Optional[ProductType] = None
    """Type of product."""

    taxAmount: Optional[int] = None
    """Tax on the line item, with the last two digits implied as decimal places.
    @minimum 0
    @maximum 2147483647"""

    taxAmountPerUnit: Optional[bool] = None
    """This field indicates if the `taxAmount` is to be interpreted as the tax 
    amount per unit rather than for the entire line item.
    This field is included in the response only when `taxAmount` is set; otherwise, 
    it will return as `null`."""

    productUrl: Optional[str] = None
    """URL of the product in the shop. Used for PAYONE Buy Now, Pay Later (BNPL)."""

    productImageUrl: Optional[str] = None
    """URL of a product image. Used for PAYONE Buy Now, Pay Later (BNPL)."""

    productCategoryPath: Optional[str] = None
    """Category path of the item. Used for PAYONE Buy Now, Pay Later (BNPL)."""

    merchantShopDeliveryReference: Optional[str] = None
    """Optional parameter to define the delivery shop or touchpoint where an item
    has been collected (e.g., for Click & Collect or Click & Reserve)."""
