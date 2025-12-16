# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

__all__ = ["MessageParam"]


class MessageParamTyped(TypedDict, total=False):
    """Message model with flexible tool support"""

    role: Required[str]
    """Role of the message sender"""

    content: Union[str, Iterable[Dict[str, object]], None]
    """Content of the message (can be null for assistant with tool_calls)"""


MessageParam: TypeAlias = Union[MessageParamTyped, Dict[str, object]]
