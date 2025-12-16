# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

from .data_config_param import DataConfigParam
from .dataset_item_param import DatasetItemParam
from .model_config_param import ModelConfigParam
from .wandb_config_param import WandbConfigParam
from .deepspeed_config_param import DeepspeedConfigParam
from .optimizer_config_param import OptimizerConfigParam
from .scheduler_config_param import SchedulerConfigParam
from .checkpoint_config_param import CheckpointConfigParam

__all__ = ["BakeConfigBaseParam"]


class BakeConfigBaseParam(TypedDict, total=False):
    """Base bake configuration fields (for responses - all optional)"""

    checkpoint: Optional[Iterable[CheckpointConfigParam]]
    """Checkpoint configuration"""

    data: Optional[DataConfigParam]
    """Data configuration for training"""

    datasets: Optional[Iterable[DatasetItemParam]]
    """List of datasets"""

    deepspeed: Optional[DeepspeedConfigParam]
    """DeepSpeed configuration"""

    epochs: Optional[int]
    """Number of epochs"""

    eval_interval: Optional[int]
    """Evaluation interval"""

    gradient_accumulation_steps: Optional[int]
    """Gradient accumulation steps"""

    micro_batch_size: Optional[int]
    """Micro batch size"""

    model: Optional[ModelConfigParam]
    """Model configuration for baking"""

    model_name: Optional[str]
    """Model name"""

    optimizer: Optional[OptimizerConfigParam]
    """Optimizer configuration"""

    scheduler: Optional[SchedulerConfigParam]
    """Learning rate scheduler configuration"""

    seed: Optional[int]
    """Random seed"""

    total_trajectories: Optional[int]
    """Total trajectories"""

    train_log_iter_interval: Optional[int]
    """Training log interval"""

    type: Optional[str]
    """Bake type (e.g., 'single_baker')"""

    wandb: Optional[WandbConfigParam]
    """Weights & Biases configuration"""
