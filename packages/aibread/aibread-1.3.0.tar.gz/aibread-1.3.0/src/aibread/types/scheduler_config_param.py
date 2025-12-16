# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["SchedulerConfigParam"]


class SchedulerConfigParam(TypedDict, total=False):
    """Learning rate scheduler configuration"""

    lr: Optional[float]
    """The initial learning rate (deprecated - use optimizer.learning_rate instead).

    This field will raise an error if set.
    """

    type: Optional[str]
    """Scheduler factory type. Defaults to trainer's scheduler_factory_type."""
