# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["GeneratorParam"]


class GeneratorParam(TypedDict, total=False):
    """Generator model"""

    type: Required[str]
    """Generator type: oneshot_qs, hardcoded, persona, from_dataset, custom"""

    dataset: Optional[str]
    """Dataset name for from_dataset"""

    max_tokens: Optional[int]
    """Maximum number of tokens to generate"""

    model: Optional[str]
    """Model name for oneshot_qs"""

    numq: Optional[int]
    """Number of questions to generate"""

    questions: Optional[SequenceNotStr[str]]
    """Hardcoded questions"""

    rollout_with_conditioned: Optional[bool]
    """
    If True, use conditioned_stimulus (v) for trajectory generation instead of
    unconditioned_stimulus (u). When set, adds trajectory_override_stimulus field to
    stimulus output. Default: false (trajectories use unconditioned stimulus).
    """

    seed: Optional[int]
    """Random seed"""

    temperature: Optional[float]
    """Generation temperature (0.0-2.0)"""

    template_content: Optional[str]
    """Template file content (for upload)"""

    template_path: Optional[str]
    """Template filename for custom generator type.

    When template_content is provided, the file is written to the repo-level
    templates/ directory (same level as prompts/, bakes/, targets/). The path is
    normalized to templates/{filename} format. Used by bake_dataset_utils to
    reference the template file during dataset generation.
    """
