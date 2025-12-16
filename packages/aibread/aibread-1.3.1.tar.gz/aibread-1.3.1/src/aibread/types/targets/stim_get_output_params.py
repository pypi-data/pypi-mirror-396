# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["StimGetOutputParams"]


class StimGetOutputParams(TypedDict, total=False):
    repo_name: Required[str]

    limit: int
    """Number of lines to return (max 1000)"""

    offset: int
    """Starting line number (0-indexed)"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""
