# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BakeDownloadParams"]


class BakeDownloadParams(TypedDict, total=False):
    repo_name: Required[str]

    checkpoint: Optional[int]
    """Checkpoint number (defaults to latest)"""

    expires_in: Optional[int]
    """URL expiry in seconds (1-604800, default 3600)"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""
