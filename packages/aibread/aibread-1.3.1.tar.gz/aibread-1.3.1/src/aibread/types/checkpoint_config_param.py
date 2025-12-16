# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["CheckpointConfigParam"]


class CheckpointConfigParam(TypedDict, total=False):
    """Checkpoint configuration"""

    auto_resume: Optional[bool]
    """If a checkpoint is found in output_dir, resume training from that checkpoint"""

    enabled: Optional[bool]
    """Enable this checkpoint engine"""

    output_dir: Optional[str]
    """Output directory for checkpoints (will be resolved to Path)"""

    save_end_of_training: Optional[bool]
    """Whether to save a checkpoint at the end of training"""

    save_every_n_epochs: Optional[int]
    """How often to trigger a checkpoint save by training epoch count"""

    save_every_n_steps: Optional[int]
    """How often to trigger a checkpoint save by training global step count"""

    type: Optional[str]
    """Checkpoint engine type"""
