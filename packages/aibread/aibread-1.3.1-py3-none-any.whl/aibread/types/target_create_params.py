# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .target_config_base_param import TargetConfigBaseParam

__all__ = ["TargetCreateParams"]


class TargetCreateParams(TypedDict, total=False):
    target_name: Required[str]
    """Name of the target"""

    template: Required[str]
    """Template: 'default' or existing target name"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    overrides: Optional[TargetConfigBaseParam]
    """Target configuration base model"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""
