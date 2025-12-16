# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["RepoListParams"]


class RepoListParams(TypedDict, total=False):
    include_metadata: bool
    """Include base_model metadata for each repo"""

    limit: Optional[int]
    """Page size for pagination (only used with include_metadata=true)"""

    offset: int
    """Starting offset for pagination (only used with include_metadata=true)"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""
