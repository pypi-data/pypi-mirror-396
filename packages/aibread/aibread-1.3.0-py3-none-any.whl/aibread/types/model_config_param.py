# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import TypedDict

__all__ = ["ModelConfigParam", "BakedAdapterConfig"]


class BakedAdapterConfig(TypedDict, total=False):
    """LoRA adapter configuration"""

    bias: Optional[str]
    """Bias setting (e.g., 'none')"""

    lora_alpha: Optional[int]
    """LoRA alpha parameter"""

    lora_dropout: Optional[float]
    """LoRA dropout rate"""

    r: Optional[int]
    """LoRA rank"""

    target_modules: Optional[str]
    """Target modules (e.g., 'all-linear')"""


class ModelConfigParam(TypedDict, total=False):
    """Model configuration for baking"""

    attn_implementation: Optional[str]
    """Attention implementation to use (e.g., 'sdpa', 'flash_attention_2')"""

    baked_adapter_config: Optional[BakedAdapterConfig]
    """LoRA adapter configuration"""

    disable_activation_checkpoint: Optional[bool]
    """Disable the use of activation checkpointing"""

    dtype: Optional[str]
    """Data type for model weights (e.g., 'bf16', 'fp16', 'fp32')"""

    parent_model_name: Optional[str]
    """
    Parent model name (e.g., 'user/repo/bake_name/checkpoint' or base model like
    'Qwen/Qwen3-32B')
    """

    peft_config: Optional[Dict[str, object]]
    """Configuration for Parameter Efficient Fine Tuning"""

    save_name: Optional[str]
    """Name to use when saving the model"""

    type: Optional[str]
    """Model factory type"""
