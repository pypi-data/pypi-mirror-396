# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

__all__ = ["OptimizerConfigParam"]


class OptimizerConfigParam(TypedDict, total=False):
    """Optimizer configuration"""

    betas: Optional[Iterable[object]]
    """
    Tuple of coefficients used for computing running averages of gradient and its
    square (e.g., (beta1, beta2) for Adam).
    """

    learning_rate: Optional[float]
    """The initial learning rate"""

    type: Optional[str]
    """Optimizer factory type. Defaults to trainer's optimizer_factory_type."""

    weight_decay: Optional[float]
    """Coefficient for L2 regularization applied to the optimizer's weights."""
