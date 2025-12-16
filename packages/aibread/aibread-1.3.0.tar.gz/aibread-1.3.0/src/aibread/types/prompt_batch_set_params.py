# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .message_param import MessageParam

__all__ = ["PromptBatchSetParams"]


class PromptBatchSetParams(TypedDict, total=False):
    prompts: Required[Dict[str, Iterable[MessageParam]]]
    """Dictionary mapping prompt_name to messages list"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""
