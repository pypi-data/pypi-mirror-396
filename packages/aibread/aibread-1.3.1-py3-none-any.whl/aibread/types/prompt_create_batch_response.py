# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from .._models import BaseModel

__all__ = ["PromptCreateBatchResponse"]


class PromptCreateBatchResponse(BaseModel):
    """Batch prompt response model"""

    created: List[str]
    """List of successfully created items"""

    failed: Dict[str, str]
    """Dictionary of failed items with error messages"""
