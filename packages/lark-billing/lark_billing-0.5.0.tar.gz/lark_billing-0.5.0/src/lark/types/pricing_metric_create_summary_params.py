# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr
from .period_param import PeriodParam

__all__ = ["PricingMetricCreateSummaryParams"]


class PricingMetricCreateSummaryParams(TypedDict, total=False):
    period: Required[PeriodParam]
    """The period that the summary should be computed over."""

    subject_id: Required[str]
    """The ID or external ID of the subject that the summary should be computed for."""

    dimensions: Optional[SequenceNotStr[str]]
    """The dimensions by which the events are grouped to compute the pricing metric."""

    period_granularity: Optional[Literal["hour", "day", "week"]]
    """The granularity of the period that the summary should be computed over."""
