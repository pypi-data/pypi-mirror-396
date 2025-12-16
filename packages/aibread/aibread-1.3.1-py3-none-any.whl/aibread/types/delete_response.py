# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["DeleteResponse"]


class DeleteResponse(BaseModel):
    """Standard delete operation response"""

    message: str
    """Success message confirming deletion"""
