# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from .._models import BaseModel

__all__ = ["BakeCreateBatchResponse"]


class BakeCreateBatchResponse(BaseModel):
    """Batch bake response"""

    created: List[str]
    """List of successfully created items"""

    failed: Dict[str, str]
    """Dictionary of failed items with error messages"""
