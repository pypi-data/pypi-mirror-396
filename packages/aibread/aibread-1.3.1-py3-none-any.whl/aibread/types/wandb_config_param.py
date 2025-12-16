# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["WandbConfigParam"]


class WandbConfigParam(TypedDict, total=False):
    """Weights & Biases configuration"""

    enable: Optional[bool]
    """Enable wandb logging"""

    entity: Optional[str]
    """Wandb entity/team"""

    name: Optional[str]
    """Run name"""

    project: Optional[str]
    """Wandb project name"""
