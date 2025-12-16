# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

from .data_source_param import DataSourceParam

__all__ = ["DataConfigParam"]


class DataConfigParam(TypedDict, total=False):
    """Data configuration for training"""

    beta: Optional[float]
    """Beta parameter for training"""

    cache_dir: Optional[str]
    """Cache directory"""

    cache_fs_type: Optional[str]
    """Cache filesystem type: 'auto', 'local', or 'shared'"""

    dl_num_workers: Optional[int]
    """Number of dataloader workers per GPU"""

    eval_sources: Optional[Iterable[DataSourceParam]]
    """List of data sources to use for evaluation"""

    max_length: Optional[int]
    """Maximum sequence length"""

    num_proc: Optional[int]
    """Number of processes to use for data loading"""

    seed: Optional[int]
    """Seed for data loading"""

    sources: Optional[Iterable[DataSourceParam]]
    """List of data sources"""

    temperature: Optional[float]
    """Sampling temperature"""

    train_eval_split: Optional[Iterable[float]]
    """Train/eval split ratio [train, eval]"""

    type: Optional[str]
    """Data type (e.g., 'single_baker')"""

    use_data_cache: Optional[bool]
    """Whether to cache loaded data. Deprecated - data cache is used by default now."""
