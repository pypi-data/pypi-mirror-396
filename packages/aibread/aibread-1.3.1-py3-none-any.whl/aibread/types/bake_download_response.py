# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["BakeDownloadResponse"]


class BakeDownloadResponse(BaseModel):
    """Presigned URL response for downloading model weights"""

    bake_name: str
    """Bake name"""

    checkpoint: int
    """Checkpoint number"""

    expires_in: int
    """URL expiry time in seconds"""

    url: str
    """Presigned URL for downloading weights"""
