# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["RecipeGetDependencyGraphResponse"]


class RecipeGetDependencyGraphResponse(BaseModel):
    """Dependency graph for a bake.

    Represents the complete dependency graph including all parent bakes,
    targets, prompts, and their relationships. Built using BFS traversal
    starting from the specified bake.
    """

    bakes: Dict[str, Dict[str, object]]
    """Dictionary of bake configs (collation + bake)"""

    base_model: str
    """Base model name"""

    edges: List[List[object]]
    """List of dependency edges (source_type, source_name, target_type, target_name)"""

    prompts: Dict[str, Optional[str]]
    """Dictionary of prompt names to file paths"""

    targets: Dict[str, Dict[str, object]]
    """Dictionary of target configs (stim + rollout)"""
