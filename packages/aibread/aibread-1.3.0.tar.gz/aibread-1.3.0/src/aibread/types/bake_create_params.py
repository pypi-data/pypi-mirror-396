# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .bake_config_base_param import BakeConfigBaseParam

__all__ = ["BakeCreateParams"]


class BakeCreateParams(TypedDict, total=False):
    bake_name: Required[str]
    """Name of the bake"""

    template: Required[str]
    """Template: 'default' or existing bake name"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    overrides: Optional[BakeConfigBaseParam]
    """Base bake configuration fields (for responses - all optional)"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""
