# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["DeepspeedConfigParam", "ZeroOptimization"]


class ZeroOptimization(TypedDict, total=False):
    """DeepSpeed ZeRO optimization configuration"""

    stage: Optional[int]
    """ZeRO stage (0, 1, 2, or 3)"""


class DeepspeedConfigParam(TypedDict, total=False):
    """DeepSpeed configuration"""

    zero_optimization: Optional[ZeroOptimization]
    """DeepSpeed ZeRO optimization configuration"""
