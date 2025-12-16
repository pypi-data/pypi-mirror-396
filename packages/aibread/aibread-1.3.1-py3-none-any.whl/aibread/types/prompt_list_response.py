# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["PromptListResponse"]


class PromptListResponse(BaseModel):
    """Prompt list model"""

    prompts: List[str]
    """List of prompt names"""
