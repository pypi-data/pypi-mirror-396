# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["DataSourceParam"]


class DataSourceParam(TypedDict, total=False):
    """Individual data source configuration"""

    max_samples: Optional[int]
    """Maximum samples to use (-1 for all)"""

    name_or_path: Optional[str]
    """Path to data file"""

    process: Optional[bool]
    """
    Whether to process the data with the data factory process function (e.g.,
    tokenization for SFTDataFactory).
    """

    sample_count: Optional[int]
    """Number of examples to randomly sample. If None, all examples are used."""

    sample_ratio: Optional[float]
    """Ratio of the dataset to randomly sample. If None, all examples are used."""

    sample_seed: Optional[int]
    """Seed for random sampling. Used only if sample_ratio or sample_count is set."""

    split: Optional[str]
    """Split to load (e.g., 'train' or 'eval').

    Defaults to 'train' for training sources, 'eval' for eval sources.
    """

    type: Optional[str]
    """Source type (e.g., 'bake_jsonl')"""
