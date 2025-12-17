# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .amount_output import AmountOutput

__all__ = ["PackagePriceOutput"]


class PackagePriceOutput(BaseModel):
    """Package price is a price that is charged for a fixed number of units.

    For example, $10 per 1000 units. If the quantity is not a multiple of the package units, the rounding behavior will be applied.
    """

    amount: AmountOutput

    package_units: int

    rounding_behavior: Literal["round_up", "round_down"]

    price_type: Optional[Literal["package"]] = None
