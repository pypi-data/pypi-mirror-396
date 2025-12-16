# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .target_config_base_param import TargetConfigBaseParam

__all__ = ["TargetBatchSetParams", "Target"]


class TargetBatchSetParams(TypedDict, total=False):
    targets: Required[Iterable[Target]]
    """List of targets to create/update"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""


class Target(TypedDict, total=False):
    """Target configuration with explicit name for batch operations"""

    target_name: Required[str]
    """Target name"""

    template: Required[str]
    """Template: 'default' or existing target name"""

    overrides: Optional[TargetConfigBaseParam]
    """Target configuration base model"""
