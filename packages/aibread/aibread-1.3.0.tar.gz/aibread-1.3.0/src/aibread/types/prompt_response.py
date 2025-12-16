# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .message import Message
from .._models import BaseModel

__all__ = ["PromptResponse"]


class PromptResponse(BaseModel):
    """Prompt response model"""

    messages: List[Message]
    """List of messages in the prompt"""

    prompt_name: str
    """Prompt identifier"""

    tools: Optional[List[Dict[str, object]]] = None
    """List of available tools/functions (OpenAI format)"""
