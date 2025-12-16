# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["RepoGetTreeResponse", "Bakes"]


class Bakes(BaseModel):
    """A node in the repository tree representing a single bake."""

    config: Dict[str, object]
    """Bake configuration (bake.yml)"""

    status: str
    """Bake status: complete, failed, running, pending, unknown"""

    checkpoints: Optional[List[int]] = None
    """List of checkpoint numbers"""

    api_model_name: Optional[List[str]] = FieldInfo(alias="model_name", default=None)
    """List of full model paths with checkpoints"""


class RepoGetTreeResponse(BaseModel):
    """Complete model lineage tree for a repository.

    Provides a full view of all bakes in the repository and their parent-child
    relationships, showing the complete model evolution tree.
    """

    bakes: Dict[str, Bakes]
    """Dictionary of all bakes in the repository"""

    base_model: str
    """Base model name (e.g., 'Qwen/Qwen3-32B')"""

    edges: List[List[str]]
    """
    List of parent-child edges: [source_type, source_name, target_type, target_name]
    """
