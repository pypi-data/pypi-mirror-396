# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SeoExperimentResultListParams"]


class SeoExperimentResultListParams(TypedDict, total=False):
    experiment_id: Required[int]
    """Experiment ID"""

    cursor: str
    """The pagination cursor value."""
