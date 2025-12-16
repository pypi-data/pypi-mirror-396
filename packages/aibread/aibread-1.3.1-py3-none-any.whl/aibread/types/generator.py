# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["Generator"]


class Generator(BaseModel):
    """Generator model"""

    type: str
    """Generator type: oneshot_qs, hardcoded, persona, from_dataset, custom"""

    dataset: Optional[str] = None
    """Dataset name for from_dataset"""

    max_tokens: Optional[int] = None
    """Maximum number of tokens to generate"""

    model: Optional[str] = None
    """Model name for oneshot_qs"""

    numq: Optional[int] = None
    """Number of questions to generate"""

    questions: Optional[List[str]] = None
    """Hardcoded questions"""

    rollout_with_conditioned: Optional[bool] = None
    """
    If True, use conditioned_stimulus (v) for trajectory generation instead of
    unconditioned_stimulus (u). When set, adds trajectory_override_stimulus field to
    stimulus output. Default: false (trajectories use unconditioned stimulus).
    """

    seed: Optional[int] = None
    """Random seed"""

    temperature: Optional[float] = None
    """Generation temperature (0.0-2.0)"""

    template_content: Optional[str] = None
    """Template file content (for upload)"""

    template_path: Optional[str] = None
    """Template filename for custom generator type.

    When template_content is provided, the file is written to the repo-level
    templates/ directory (same level as prompts/, bakes/, targets/). The path is
    normalized to templates/{filename} format. Used by bake_dataset_utils to
    reference the template file during dataset generation.
    """
