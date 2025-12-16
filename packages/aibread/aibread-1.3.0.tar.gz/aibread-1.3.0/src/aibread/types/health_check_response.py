# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["HealthCheckResponse"]


class HealthCheckResponse(BaseModel):
    """Health check response"""

    api: str
    """API name"""

    status: str
    """API health status: 'healthy' or 'degraded'"""

    version: str
    """API version"""
