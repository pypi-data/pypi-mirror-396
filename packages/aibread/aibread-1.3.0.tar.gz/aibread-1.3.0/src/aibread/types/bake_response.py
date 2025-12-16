# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["BakeResponse"]


class BakeResponse(BaseModel):
    """Bake response: Inherits all fields from JobStatus"""

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

    loss: Optional[Dict[str, float]] = None
    """Loss values from training.

    Contains 'latest_loss', 'final_loss', 'min_loss', 'max_loss'. Present when
    status is 'running' or 'complete' and metrics are available
    """

    api_model_name: Optional[List[str]] = FieldInfo(alias="model_name", default=None)
    """List of model names in format 'user/repo/bake_name/checkpoint'.

    Index 0 is the latest checkpoint. Only present when status is 'complete'
    """

    progress_percent: Optional[float] = None
    """Job progress percentage (0-100) if job is running"""
