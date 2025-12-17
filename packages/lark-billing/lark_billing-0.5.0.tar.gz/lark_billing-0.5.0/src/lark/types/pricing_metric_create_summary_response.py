# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import TypeAlias

from .period import Period
from .._models import BaseModel

__all__ = ["PricingMetricCreateSummaryResponse", "PricingMetricCreateSummaryResponseItem"]


class PricingMetricCreateSummaryResponseItem(BaseModel):
    id: str
    """The ID of the pricing metric summary."""

    dimension_coordinates: Optional[Dict[str, str]] = None
    """The dimension coordinates that the summary is for."""

    period: Period
    """The period that the summary is computed over."""

    pricing_metric_id: str
    """The ID of the pricing metric that the summary is for."""

    subject_id: str
    """The ID of the subject that the summary is for."""

    value: Optional[str] = None
    """The computed value of the pricing metric for the period.

    If the pricing metric does not have any usage events for the period, this will
    be `null`.
    """


PricingMetricCreateSummaryResponse: TypeAlias = List[PricingMetricCreateSummaryResponseItem]
