# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import TypedDict

from .generator_param import GeneratorParam

__all__ = ["TargetConfigBaseParam"]


class TargetConfigBaseParam(TypedDict, total=False):
    """Target configuration base model"""

    extra_kwargs: Optional[Dict[str, object]]
    """Additional kwargs passed to chat.completions.create()"""

    generators: Optional[Iterable[GeneratorParam]]
    """Data generation strategies"""

    max_concurrency: Optional[int]
    """Maximum concurrent requests"""

    max_tokens: Optional[int]
    """Maximum tokens to generate"""

    model_name: Optional[str]
    """Base model for rollout"""

    num_traj_per_stimulus: Optional[int]
    """Number of trajectories per stimulus"""

    student_prompt: Optional[str]
    """Student prompt name (conditioned stimulus)"""

    teacher_prompt: Optional[str]
    """Teacher prompt name (unconditioned stimulus)"""

    temperature: Optional[float]
    """Generation temperature (0.0-2.0)"""

    u: Optional[str]
    """[DEPRECATED] Use 'teacher_prompt' instead. Unconditioned stimulus prompt name."""

    v: Optional[str]
    """[DEPRECATED] Use 'student_prompt' instead. Conditioned stimulus prompt name."""
