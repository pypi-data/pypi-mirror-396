# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .bake_config_base_param import BakeConfigBaseParam

__all__ = ["BakeCreateBatchParams", "Bake"]


class BakeCreateBatchParams(TypedDict, total=False):
    bakes: Required[Iterable[Bake]]
    """List of bakes to create/update"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""


class Bake(TypedDict, total=False):
    """Bake configuration with explicit name for batch operations"""

    bake_name: Required[str]
    """Bake name"""

    template: Required[str]
    """Template: 'default' or existing bake name"""

    overrides: Optional[BakeConfigBaseParam]
    """Base bake configuration fields (for responses - all optional)"""
