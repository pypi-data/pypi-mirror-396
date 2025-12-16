# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["RolloutResponse"]


class RolloutResponse(BaseModel):
    """Rollout job execution status

    Inherits all fields from JobStatus. Separated from StimResponse
    for future extensibility (e.g., model checkpoint paths, inference metrics).
    """

    status: str
    """Job status: not_started, running, complete, failed"""

    config: Optional[Dict[str, object]] = None
    """Job config parameters"""

    error: Optional[str] = None
    """Error message if job failed"""

    job_id: Optional[int] = None
    """Coordinator job ID (if job is queued/running)"""

    lines: Optional[int] = None
    """Number of output lines (not applicable for bakes)"""

    progress_percent: Optional[float] = None
    """Job progress percentage (0-100) if job is running"""
