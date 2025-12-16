# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DatasetItemParam"]


class DatasetItemParam(TypedDict, total=False):
    """Dataset reference for collation (API-facing, simplified)"""

    target: Required[str]
    """Target name"""

    weight: float
    """Dataset weight"""
