# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .message_param import MessageParam

__all__ = ["PromptSetParams"]


class PromptSetParams(TypedDict, total=False):
    repo_name: Required[str]

    messages: Required[Iterable[MessageParam]]
    """List of messages in the prompt"""

    user_id: Optional[str]
    """User ID override (requires master API key)"""

    tools: Optional[Iterable[Dict[str, object]]]
    """List of available tools/functions (OpenAI format)"""

    x_user_id: Annotated[str, PropertyInfo(alias="X-User-Id")]
    """User ID override via header (requires master API key)"""
