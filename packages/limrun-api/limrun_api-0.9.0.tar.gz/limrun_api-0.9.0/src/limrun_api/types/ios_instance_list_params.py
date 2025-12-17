# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["IosInstanceListParams"]


class IosInstanceListParams(TypedDict, total=False):
    ending_before: Annotated[str, PropertyInfo(alias="endingBefore")]

    label_selector: Annotated[str, PropertyInfo(alias="labelSelector")]
    """
    Labels filter to apply to instances to return. Expects a comma-separated list of
    key=value pairs (e.g., env=prod,region=us-west).
    """

    limit: int
    """Maximum number of items to be returned. The default is 50."""

    region: str
    """Region where the instance is scheduled on."""

    starting_after: Annotated[str, PropertyInfo(alias="startingAfter")]

    state: str
    """State filter to apply to Android instances to return.

    Each comma-separated state will be used as part of an OR clause, e.g.
    "assigned,ready" will return all instances that are either assigned or ready.

    Valid states: creating, assigned, ready, terminated, unknown
    """
