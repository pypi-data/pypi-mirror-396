# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["RecipeGetRecreationPlanResponse", "Resources", "ResourcesBake", "Step"]


class ResourcesBake(BaseModel):
    """Bake resource with model names"""

    bake_name: str
    """Name of the bake"""

    api_model_names: Optional[List[str]] = FieldInfo(alias="model_names", default=None)
    """List of model names (checkpoints) for this bake"""


class Resources(BaseModel):
    """Summary of all resources"""

    bakes: List[ResourcesBake]
    """List of bake resources with model names"""

    prompts: List[str]
    """List of prompt names"""

    targets: List[str]
    """List of target names"""


class Step(BaseModel):
    """A single step in the recreation plan.

    Represents one action needed to recreate a bake, including its dependencies
    and configuration.
    """

    action: str
    """
    Action to perform: create_prompt, create_target, run_stim, run_rollout,
    create_bake, run_bake
    """

    config: Dict[str, object]
    """Configuration for this resource (cleaned, no internal paths)"""

    dependencies: List[str]
    """
    List of dependencies in format 'resource_type:resource_name' or
    'resource_type:resource_name:status'
    """

    resource_name: str
    """Name of the resource"""

    resource_type: str
    """Type of resource: prompt, target, or bake"""

    step: int
    """Step number in execution order"""


class RecipeGetRecreationPlanResponse(BaseModel):
    """Recreation plan for a bake.

    A complete step-by-step plan to recreate a bake, including all dependencies
    in the correct execution order. The plan is topologically sorted to ensure
    dependencies are created before dependents.
    """

    base_model: str
    """Base model name (e.g., 'Qwen/Qwen3-32B')"""

    resources: Resources
    """Summary of all resources"""

    steps: List[Step]
    """Ordered list of steps to recreate the bake"""

    total_steps: int
    """Total number of steps"""
