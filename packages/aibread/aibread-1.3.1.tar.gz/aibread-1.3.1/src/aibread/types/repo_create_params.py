# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["RepoCreateParams"]


class RepoCreateParams(TypedDict, total=False):
    repo_name: Required[str]
    """Name of the repository"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    base_model: Optional[str]
    """Base model for the repository (optional)"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""
