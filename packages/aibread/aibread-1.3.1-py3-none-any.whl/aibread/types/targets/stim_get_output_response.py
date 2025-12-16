# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ..._models import BaseModel

__all__ = ["StimGetOutputResponse"]


class StimGetOutputResponse(BaseModel):
    """Paginated stim output response

    Returns stim job status along with paginated output data.
    """

    has_more: bool
    """Whether more data is available"""

    limit: int
    """Page size"""

    offset: int
    """Starting line offset"""

    output: List[Dict[str, object]]
    """Paginated output data"""

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
