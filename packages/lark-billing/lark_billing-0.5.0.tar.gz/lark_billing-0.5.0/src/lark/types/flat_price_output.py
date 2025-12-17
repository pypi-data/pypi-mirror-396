# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .amount_output import AmountOutput

__all__ = ["FlatPriceOutput"]


class FlatPriceOutput(BaseModel):
    """Flat price is a price that linearly scales with the quantity."""

    amount: AmountOutput

    price_type: Optional[Literal["flat"]] = None
