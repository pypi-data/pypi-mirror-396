# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from aibread import Bread, AsyncBread
from tests.utils import assert_matches_type
from aibread.types import (
    BakeResponse,
    DeleteResponse,
    BakeListResponse,
    BakeBatchSetResponse,
    BakeDownloadResponse,
    BakeGetMetricsResponse,
    BakeCreateBatchResponse,
)

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBakes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Bread) -> None:
        bake = client.bakes.create(
            repo_name="repo_name",
            bake_name="bake_name",
            template="template",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Bread) -> None:
        bake = client.bakes.create(
            repo_name="repo_name",
            bake_name="bake_name",
            template="template",
            user_id="user_id",
            overrides={
                "checkpoint": [
                    {
                        "auto_resume": True,
                        "enabled": True,
                        "output_dir": "output_dir",
                        "save_end_of_training": True,
                        "save_every_n_epochs": 0,
                        "save_every_n_steps": 0,
                        "type": "type",
                    }
                ],
                "data": {
                    "beta": 0,
                    "cache_dir": "cache_dir",
                    "cache_fs_type": "cache_fs_type",
                    "dl_num_workers": 0,
                    "eval_sources": [
                        {
                            "max_samples": 0,
                            "name_or_path": "name_or_path",
                            "process": True,
                            "sample_count": 0,
                            "sample_ratio": 0,
                            "sample_seed": 0,
                            "split": "split",
                            "type": "type",
                        }
                    ],
                    "max_length": 0,
                    "num_proc": 0,
                    "seed": 0,
                    "sources": [
                        {
                            "max_samples": 0,
                            "name_or_path": "name_or_path",
                            "process": True,
                            "sample_count": 0,
                            "sample_ratio": 0,
                            "sample_seed": 0,
                            "split": "split",
                            "type": "type",
                        }
                    ],
                    "temperature": 0,
                    "train_eval_split": [0],
                    "type": "type",
                    "use_data_cache": True,
                },
                "datasets": [
                    {
                        "target": "target",
                        "weight": 0,
                    }
                ],
                "deepspeed": {"zero_optimization": {"stage": 0}},
                "epochs": 0,
                "eval_interval": 0,
                "gradient_accumulation_steps": 0,
                "micro_batch_size": 0,
                "model": {
                    "attn_implementation": "attn_implementation",
                    "baked_adapter_config": {
                        "bias": "bias",
                        "lora_alpha": 0,
                        "lora_dropout": 0,
                        "r": 0,
                        "target_modules": "target_modules",
                    },
                    "disable_activation_checkpoint": True,
                    "dtype": "dtype",
                    "parent_model_name": "parent_model_name",
                    "peft_config": {"foo": "bar"},
                    "save_name": "save_name",
                    "type": "type",
                },
                "model_name": "model_name",
                "optimizer": {
                    "betas": [{}, {}],
                    "learning_rate": 0,
                    "type": "type",
                    "weight_decay": 0,
                },
                "scheduler": {
                    "lr": 0,
                    "type": "type",
                },
                "seed": 0,
                "total_trajectories": 0,
                "train_log_iter_interval": 0,
                "type": "type",
                "wandb": {
                    "enable": True,
                    "entity": "entity",
                    "name": "name",
                    "project": "project",
                },
            },
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Bread) -> None:
        response = client.bakes.with_raw_response.create(
            repo_name="repo_name",
            bake_name="bake_name",
            template="template",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Bread) -> None:
        with client.bakes.with_streaming_response.create(
            repo_name="repo_name",
            bake_name="bake_name",
            template="template",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = response.parse()
            assert_matches_type(BakeResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.bakes.with_raw_response.create(
                repo_name="",
                bake_name="bake_name",
                template="template",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Bread) -> None:
        bake = client.bakes.list(
            repo_name="repo_name",
        )
        assert_matches_type(BakeListResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Bread) -> None:
        bake = client.bakes.list(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeListResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Bread) -> None:
        response = client.bakes.with_raw_response.list(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(BakeListResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Bread) -> None:
        with client.bakes.with_streaming_response.list(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = response.parse()
            assert_matches_type(BakeListResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.bakes.with_raw_response.list(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Bread) -> None:
        bake = client.bakes.delete(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(DeleteResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: Bread) -> None:
        bake = client.bakes.delete(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(DeleteResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Bread) -> None:
        response = client.bakes.with_raw_response.delete(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(DeleteResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Bread) -> None:
        with client.bakes.with_streaming_response.delete(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = response.parse()
            assert_matches_type(DeleteResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.bakes.with_raw_response.delete(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            client.bakes.with_raw_response.delete(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            bake = client.bakes.batch_set(
                repo_name="repo_name",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                    },
                ],
            )

        assert_matches_type(BakeBatchSetResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_set_with_all_params(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            bake = client.bakes.batch_set(
                repo_name="repo_name",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                        "overrides": {
                            "checkpoint": [
                                {
                                    "auto_resume": True,
                                    "enabled": True,
                                    "output_dir": "output_dir",
                                    "save_end_of_training": True,
                                    "save_every_n_epochs": 0,
                                    "save_every_n_steps": 0,
                                    "type": "type",
                                }
                            ],
                            "data": {
                                "beta": 0,
                                "cache_dir": "cache_dir",
                                "cache_fs_type": "cache_fs_type",
                                "dl_num_workers": 0,
                                "eval_sources": [
                                    {
                                        "max_samples": 0,
                                        "name_or_path": "name_or_path",
                                        "process": True,
                                        "sample_count": 0,
                                        "sample_ratio": 0,
                                        "sample_seed": 0,
                                        "split": "split",
                                        "type": "type",
                                    }
                                ],
                                "max_length": 0,
                                "num_proc": 0,
                                "seed": 0,
                                "sources": [
                                    {
                                        "max_samples": 0,
                                        "name_or_path": "name_or_path",
                                        "process": True,
                                        "sample_count": 0,
                                        "sample_ratio": 0,
                                        "sample_seed": 0,
                                        "split": "split",
                                        "type": "type",
                                    }
                                ],
                                "temperature": 0,
                                "train_eval_split": [0],
                                "type": "type",
                                "use_data_cache": True,
                            },
                            "datasets": [
                                {
                                    "target": "target",
                                    "weight": 0,
                                }
                            ],
                            "deepspeed": {"zero_optimization": {"stage": 0}},
                            "epochs": 5,
                            "eval_interval": 0,
                            "gradient_accumulation_steps": 0,
                            "micro_batch_size": 16,
                            "model": {
                                "attn_implementation": "attn_implementation",
                                "baked_adapter_config": {
                                    "bias": "bias",
                                    "lora_alpha": 0,
                                    "lora_dropout": 0,
                                    "r": 0,
                                    "target_modules": "target_modules",
                                },
                                "disable_activation_checkpoint": True,
                                "dtype": "dtype",
                                "parent_model_name": "parent_model_name",
                                "peft_config": {"foo": "bar"},
                                "save_name": "save_name",
                                "type": "type",
                            },
                            "model_name": "model_name",
                            "optimizer": {
                                "betas": [{}, {}],
                                "learning_rate": 0,
                                "type": "type",
                                "weight_decay": 0,
                            },
                            "scheduler": {
                                "lr": 0,
                                "type": "type",
                            },
                            "seed": 0,
                            "total_trajectories": 0,
                            "train_log_iter_interval": 0,
                            "type": "type",
                            "wandb": {
                                "enable": True,
                                "entity": "entity",
                                "name": "name",
                                "project": "project",
                            },
                        },
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                        "overrides": {
                            "checkpoint": [
                                {
                                    "auto_resume": True,
                                    "enabled": True,
                                    "output_dir": "output_dir",
                                    "save_end_of_training": True,
                                    "save_every_n_epochs": 0,
                                    "save_every_n_steps": 0,
                                    "type": "type",
                                }
                            ],
                            "data": {
                                "beta": 0,
                                "cache_dir": "cache_dir",
                                "cache_fs_type": "cache_fs_type",
                                "dl_num_workers": 0,
                                "eval_sources": [
                                    {
                                        "max_samples": 0,
                                        "name_or_path": "name_or_path",
                                        "process": True,
                                        "sample_count": 0,
                                        "sample_ratio": 0,
                                        "sample_seed": 0,
                                        "split": "split",
                                        "type": "type",
                                    }
                                ],
                                "max_length": 0,
                                "num_proc": 0,
                                "seed": 0,
                                "sources": [
                                    {
                                        "max_samples": 0,
                                        "name_or_path": "name_or_path",
                                        "process": True,
                                        "sample_count": 0,
                                        "sample_ratio": 0,
                                        "sample_seed": 0,
                                        "split": "split",
                                        "type": "type",
                                    }
                                ],
                                "temperature": 0,
                                "train_eval_split": [0],
                                "type": "type",
                                "use_data_cache": True,
                            },
                            "datasets": [
                                {
                                    "target": "target",
                                    "weight": 0,
                                }
                            ],
                            "deepspeed": {"zero_optimization": {"stage": 0}},
                            "epochs": 0,
                            "eval_interval": 0,
                            "gradient_accumulation_steps": 0,
                            "micro_batch_size": 0,
                            "model": {
                                "attn_implementation": "attn_implementation",
                                "baked_adapter_config": {
                                    "bias": "bias",
                                    "lora_alpha": 0,
                                    "lora_dropout": 0,
                                    "r": 0,
                                    "target_modules": "target_modules",
                                },
                                "disable_activation_checkpoint": True,
                                "dtype": "dtype",
                                "parent_model_name": "parent_model_name",
                                "peft_config": {"foo": "bar"},
                                "save_name": "save_name",
                                "type": "type",
                            },
                            "model_name": "model_name",
                            "optimizer": {
                                "betas": [{}, {}],
                                "learning_rate": 0.001,
                                "type": "type",
                                "weight_decay": 0,
                            },
                            "scheduler": {
                                "lr": 0,
                                "type": "type",
                            },
                            "seed": 0,
                            "total_trajectories": 0,
                            "train_log_iter_interval": 0,
                            "type": "type",
                            "wandb": {
                                "enable": True,
                                "entity": "entity",
                                "name": "name",
                                "project": "project",
                            },
                        },
                    },
                ],
                user_id="user_id",
                x_user_id="X-User-Id",
            )

        assert_matches_type(BakeBatchSetResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.bakes.with_raw_response.batch_set(
                repo_name="repo_name",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                    },
                ],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(BakeBatchSetResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.bakes.with_streaming_response.batch_set(
                repo_name="repo_name",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                    },
                ],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                bake = response.parse()
                assert_matches_type(BakeBatchSetResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                client.bakes.with_raw_response.batch_set(
                    repo_name="",
                    bakes=[
                        {
                            "bake_name": "bake_v1",
                            "template": "default",
                        },
                        {
                            "bake_name": "bake_v2",
                            "template": "bake_v1",
                        },
                    ],
                )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_batch(self, client: Bread) -> None:
        bake = client.bakes.create_batch(
            repo_name="repo_name",
            bakes=[
                {
                    "bake_name": "bake_v1",
                    "template": "default",
                },
                {
                    "bake_name": "bake_v2",
                    "template": "bake_v1",
                },
            ],
        )
        assert_matches_type(BakeCreateBatchResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_batch_with_all_params(self, client: Bread) -> None:
        bake = client.bakes.create_batch(
            repo_name="repo_name",
            bakes=[
                {
                    "bake_name": "bake_v1",
                    "template": "default",
                    "overrides": {
                        "checkpoint": [
                            {
                                "auto_resume": True,
                                "enabled": True,
                                "output_dir": "output_dir",
                                "save_end_of_training": True,
                                "save_every_n_epochs": 0,
                                "save_every_n_steps": 0,
                                "type": "type",
                            }
                        ],
                        "data": {
                            "beta": 0,
                            "cache_dir": "cache_dir",
                            "cache_fs_type": "cache_fs_type",
                            "dl_num_workers": 0,
                            "eval_sources": [
                                {
                                    "max_samples": 0,
                                    "name_or_path": "name_or_path",
                                    "process": True,
                                    "sample_count": 0,
                                    "sample_ratio": 0,
                                    "sample_seed": 0,
                                    "split": "split",
                                    "type": "type",
                                }
                            ],
                            "max_length": 0,
                            "num_proc": 0,
                            "seed": 0,
                            "sources": [
                                {
                                    "max_samples": 0,
                                    "name_or_path": "name_or_path",
                                    "process": True,
                                    "sample_count": 0,
                                    "sample_ratio": 0,
                                    "sample_seed": 0,
                                    "split": "split",
                                    "type": "type",
                                }
                            ],
                            "temperature": 0,
                            "train_eval_split": [0],
                            "type": "type",
                            "use_data_cache": True,
                        },
                        "datasets": [
                            {
                                "target": "target",
                                "weight": 0,
                            }
                        ],
                        "deepspeed": {"zero_optimization": {"stage": 0}},
                        "epochs": 5,
                        "eval_interval": 0,
                        "gradient_accumulation_steps": 0,
                        "micro_batch_size": 16,
                        "model": {
                            "attn_implementation": "attn_implementation",
                            "baked_adapter_config": {
                                "bias": "bias",
                                "lora_alpha": 0,
                                "lora_dropout": 0,
                                "r": 0,
                                "target_modules": "target_modules",
                            },
                            "disable_activation_checkpoint": True,
                            "dtype": "dtype",
                            "parent_model_name": "parent_model_name",
                            "peft_config": {"foo": "bar"},
                            "save_name": "save_name",
                            "type": "type",
                        },
                        "model_name": "model_name",
                        "optimizer": {
                            "betas": [{}, {}],
                            "learning_rate": 0,
                            "type": "type",
                            "weight_decay": 0,
                        },
                        "scheduler": {
                            "lr": 0,
                            "type": "type",
                        },
                        "seed": 0,
                        "total_trajectories": 0,
                        "train_log_iter_interval": 0,
                        "type": "type",
                        "wandb": {
                            "enable": True,
                            "entity": "entity",
                            "name": "name",
                            "project": "project",
                        },
                    },
                },
                {
                    "bake_name": "bake_v2",
                    "template": "bake_v1",
                    "overrides": {
                        "checkpoint": [
                            {
                                "auto_resume": True,
                                "enabled": True,
                                "output_dir": "output_dir",
                                "save_end_of_training": True,
                                "save_every_n_epochs": 0,
                                "save_every_n_steps": 0,
                                "type": "type",
                            }
                        ],
                        "data": {
                            "beta": 0,
                            "cache_dir": "cache_dir",
                            "cache_fs_type": "cache_fs_type",
                            "dl_num_workers": 0,
                            "eval_sources": [
                                {
                                    "max_samples": 0,
                                    "name_or_path": "name_or_path",
                                    "process": True,
                                    "sample_count": 0,
                                    "sample_ratio": 0,
                                    "sample_seed": 0,
                                    "split": "split",
                                    "type": "type",
                                }
                            ],
                            "max_length": 0,
                            "num_proc": 0,
                            "seed": 0,
                            "sources": [
                                {
                                    "max_samples": 0,
                                    "name_or_path": "name_or_path",
                                    "process": True,
                                    "sample_count": 0,
                                    "sample_ratio": 0,
                                    "sample_seed": 0,
                                    "split": "split",
                                    "type": "type",
                                }
                            ],
                            "temperature": 0,
                            "train_eval_split": [0],
                            "type": "type",
                            "use_data_cache": True,
                        },
                        "datasets": [
                            {
                                "target": "target",
                                "weight": 0,
                            }
                        ],
                        "deepspeed": {"zero_optimization": {"stage": 0}},
                        "epochs": 0,
                        "eval_interval": 0,
                        "gradient_accumulation_steps": 0,
                        "micro_batch_size": 0,
                        "model": {
                            "attn_implementation": "attn_implementation",
                            "baked_adapter_config": {
                                "bias": "bias",
                                "lora_alpha": 0,
                                "lora_dropout": 0,
                                "r": 0,
                                "target_modules": "target_modules",
                            },
                            "disable_activation_checkpoint": True,
                            "dtype": "dtype",
                            "parent_model_name": "parent_model_name",
                            "peft_config": {"foo": "bar"},
                            "save_name": "save_name",
                            "type": "type",
                        },
                        "model_name": "model_name",
                        "optimizer": {
                            "betas": [{}, {}],
                            "learning_rate": 0.001,
                            "type": "type",
                            "weight_decay": 0,
                        },
                        "scheduler": {
                            "lr": 0,
                            "type": "type",
                        },
                        "seed": 0,
                        "total_trajectories": 0,
                        "train_log_iter_interval": 0,
                        "type": "type",
                        "wandb": {
                            "enable": True,
                            "entity": "entity",
                            "name": "name",
                            "project": "project",
                        },
                    },
                },
            ],
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeCreateBatchResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_batch(self, client: Bread) -> None:
        response = client.bakes.with_raw_response.create_batch(
            repo_name="repo_name",
            bakes=[
                {
                    "bake_name": "bake_v1",
                    "template": "default",
                },
                {
                    "bake_name": "bake_v2",
                    "template": "bake_v1",
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(BakeCreateBatchResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_batch(self, client: Bread) -> None:
        with client.bakes.with_streaming_response.create_batch(
            repo_name="repo_name",
            bakes=[
                {
                    "bake_name": "bake_v1",
                    "template": "default",
                },
                {
                    "bake_name": "bake_v2",
                    "template": "bake_v1",
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = response.parse()
            assert_matches_type(BakeCreateBatchResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_batch(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.bakes.with_raw_response.create_batch(
                repo_name="",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                    },
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_download(self, client: Bread) -> None:
        bake = client.bakes.download(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(BakeDownloadResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_download_with_all_params(self, client: Bread) -> None:
        bake = client.bakes.download(
            bake_name="bake_name",
            repo_name="repo_name",
            checkpoint=0,
            expires_in=1,
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeDownloadResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_download(self, client: Bread) -> None:
        response = client.bakes.with_raw_response.download(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(BakeDownloadResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_download(self, client: Bread) -> None:
        with client.bakes.with_streaming_response.download(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = response.parse()
            assert_matches_type(BakeDownloadResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_download(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.bakes.with_raw_response.download(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            client.bakes.with_raw_response.download(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Bread) -> None:
        bake = client.bakes.get(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Bread) -> None:
        bake = client.bakes.get(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Bread) -> None:
        response = client.bakes.with_raw_response.get(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Bread) -> None:
        with client.bakes.with_streaming_response.get(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = response.parse()
            assert_matches_type(BakeResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.bakes.with_raw_response.get(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            client.bakes.with_raw_response.get(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_metrics(self, client: Bread) -> None:
        bake = client.bakes.get_metrics(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(BakeGetMetricsResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_metrics_with_all_params(self, client: Bread) -> None:
        bake = client.bakes.get_metrics(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeGetMetricsResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_metrics(self, client: Bread) -> None:
        response = client.bakes.with_raw_response.get_metrics(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(BakeGetMetricsResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_metrics(self, client: Bread) -> None:
        with client.bakes.with_streaming_response.get_metrics(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = response.parse()
            assert_matches_type(BakeGetMetricsResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_metrics(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.bakes.with_raw_response.get_metrics(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            client.bakes.with_raw_response.get_metrics(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run(self, client: Bread) -> None:
        bake = client.bakes.run(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_with_all_params(self, client: Bread) -> None:
        bake = client.bakes.run(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_run(self, client: Bread) -> None:
        response = client.bakes.with_raw_response.run(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_run(self, client: Bread) -> None:
        with client.bakes.with_streaming_response.run(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = response.parse()
            assert_matches_type(BakeResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_run(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.bakes.with_raw_response.run(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            client.bakes.with_raw_response.run(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            bake = client.bakes.set(
                bake_name="bake_name",
                repo_name="repo_name",
                template="template",
            )

        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_with_all_params(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            bake = client.bakes.set(
                bake_name="bake_name",
                repo_name="repo_name",
                template="template",
                user_id="user_id",
                overrides={
                    "checkpoint": [
                        {
                            "auto_resume": True,
                            "enabled": True,
                            "output_dir": "output_dir",
                            "save_end_of_training": True,
                            "save_every_n_epochs": 0,
                            "save_every_n_steps": 0,
                            "type": "type",
                        }
                    ],
                    "data": {
                        "beta": 0,
                        "cache_dir": "cache_dir",
                        "cache_fs_type": "cache_fs_type",
                        "dl_num_workers": 0,
                        "eval_sources": [
                            {
                                "max_samples": 0,
                                "name_or_path": "name_or_path",
                                "process": True,
                                "sample_count": 0,
                                "sample_ratio": 0,
                                "sample_seed": 0,
                                "split": "split",
                                "type": "type",
                            }
                        ],
                        "max_length": 0,
                        "num_proc": 0,
                        "seed": 0,
                        "sources": [
                            {
                                "max_samples": 0,
                                "name_or_path": "name_or_path",
                                "process": True,
                                "sample_count": 0,
                                "sample_ratio": 0,
                                "sample_seed": 0,
                                "split": "split",
                                "type": "type",
                            }
                        ],
                        "temperature": 0,
                        "train_eval_split": [0],
                        "type": "type",
                        "use_data_cache": True,
                    },
                    "datasets": [
                        {
                            "target": "target",
                            "weight": 0,
                        }
                    ],
                    "deepspeed": {"zero_optimization": {"stage": 0}},
                    "epochs": 0,
                    "eval_interval": 0,
                    "gradient_accumulation_steps": 0,
                    "micro_batch_size": 0,
                    "model": {
                        "attn_implementation": "attn_implementation",
                        "baked_adapter_config": {
                            "bias": "bias",
                            "lora_alpha": 0,
                            "lora_dropout": 0,
                            "r": 0,
                            "target_modules": "target_modules",
                        },
                        "disable_activation_checkpoint": True,
                        "dtype": "dtype",
                        "parent_model_name": "parent_model_name",
                        "peft_config": {"foo": "bar"},
                        "save_name": "save_name",
                        "type": "type",
                    },
                    "model_name": "model_name",
                    "optimizer": {
                        "betas": [{}, {}],
                        "learning_rate": 0,
                        "type": "type",
                        "weight_decay": 0,
                    },
                    "scheduler": {
                        "lr": 0,
                        "type": "type",
                    },
                    "seed": 0,
                    "total_trajectories": 0,
                    "train_log_iter_interval": 0,
                    "type": "type",
                    "wandb": {
                        "enable": True,
                        "entity": "entity",
                        "name": "name",
                        "project": "project",
                    },
                },
                x_user_id="X-User-Id",
            )

        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.bakes.with_raw_response.set(
                bake_name="bake_name",
                repo_name="repo_name",
                template="template",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = response.parse()
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.bakes.with_streaming_response.set(
                bake_name="bake_name",
                repo_name="repo_name",
                template="template",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                bake = response.parse()
                assert_matches_type(BakeResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                client.bakes.with_raw_response.set(
                    bake_name="bake_name",
                    repo_name="",
                    template="template",
                )

            with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
                client.bakes.with_raw_response.set(
                    bake_name="",
                    repo_name="repo_name",
                    template="template",
                )


class TestAsyncBakes:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.create(
            repo_name="repo_name",
            bake_name="bake_name",
            template="template",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.create(
            repo_name="repo_name",
            bake_name="bake_name",
            template="template",
            user_id="user_id",
            overrides={
                "checkpoint": [
                    {
                        "auto_resume": True,
                        "enabled": True,
                        "output_dir": "output_dir",
                        "save_end_of_training": True,
                        "save_every_n_epochs": 0,
                        "save_every_n_steps": 0,
                        "type": "type",
                    }
                ],
                "data": {
                    "beta": 0,
                    "cache_dir": "cache_dir",
                    "cache_fs_type": "cache_fs_type",
                    "dl_num_workers": 0,
                    "eval_sources": [
                        {
                            "max_samples": 0,
                            "name_or_path": "name_or_path",
                            "process": True,
                            "sample_count": 0,
                            "sample_ratio": 0,
                            "sample_seed": 0,
                            "split": "split",
                            "type": "type",
                        }
                    ],
                    "max_length": 0,
                    "num_proc": 0,
                    "seed": 0,
                    "sources": [
                        {
                            "max_samples": 0,
                            "name_or_path": "name_or_path",
                            "process": True,
                            "sample_count": 0,
                            "sample_ratio": 0,
                            "sample_seed": 0,
                            "split": "split",
                            "type": "type",
                        }
                    ],
                    "temperature": 0,
                    "train_eval_split": [0],
                    "type": "type",
                    "use_data_cache": True,
                },
                "datasets": [
                    {
                        "target": "target",
                        "weight": 0,
                    }
                ],
                "deepspeed": {"zero_optimization": {"stage": 0}},
                "epochs": 0,
                "eval_interval": 0,
                "gradient_accumulation_steps": 0,
                "micro_batch_size": 0,
                "model": {
                    "attn_implementation": "attn_implementation",
                    "baked_adapter_config": {
                        "bias": "bias",
                        "lora_alpha": 0,
                        "lora_dropout": 0,
                        "r": 0,
                        "target_modules": "target_modules",
                    },
                    "disable_activation_checkpoint": True,
                    "dtype": "dtype",
                    "parent_model_name": "parent_model_name",
                    "peft_config": {"foo": "bar"},
                    "save_name": "save_name",
                    "type": "type",
                },
                "model_name": "model_name",
                "optimizer": {
                    "betas": [{}, {}],
                    "learning_rate": 0,
                    "type": "type",
                    "weight_decay": 0,
                },
                "scheduler": {
                    "lr": 0,
                    "type": "type",
                },
                "seed": 0,
                "total_trajectories": 0,
                "train_log_iter_interval": 0,
                "type": "type",
                "wandb": {
                    "enable": True,
                    "entity": "entity",
                    "name": "name",
                    "project": "project",
                },
            },
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBread) -> None:
        response = await async_client.bakes.with_raw_response.create(
            repo_name="repo_name",
            bake_name="bake_name",
            template="template",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBread) -> None:
        async with async_client.bakes.with_streaming_response.create(
            repo_name="repo_name",
            bake_name="bake_name",
            template="template",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = await response.parse()
            assert_matches_type(BakeResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.bakes.with_raw_response.create(
                repo_name="",
                bake_name="bake_name",
                template="template",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.list(
            repo_name="repo_name",
        )
        assert_matches_type(BakeListResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.list(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeListResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBread) -> None:
        response = await async_client.bakes.with_raw_response.list(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(BakeListResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBread) -> None:
        async with async_client.bakes.with_streaming_response.list(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = await response.parse()
            assert_matches_type(BakeListResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.bakes.with_raw_response.list(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.delete(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(DeleteResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.delete(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(DeleteResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncBread) -> None:
        response = await async_client.bakes.with_raw_response.delete(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(DeleteResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncBread) -> None:
        async with async_client.bakes.with_streaming_response.delete(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = await response.parse()
            assert_matches_type(DeleteResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.bakes.with_raw_response.delete(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            await async_client.bakes.with_raw_response.delete(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            bake = await async_client.bakes.batch_set(
                repo_name="repo_name",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                    },
                ],
            )

        assert_matches_type(BakeBatchSetResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_set_with_all_params(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            bake = await async_client.bakes.batch_set(
                repo_name="repo_name",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                        "overrides": {
                            "checkpoint": [
                                {
                                    "auto_resume": True,
                                    "enabled": True,
                                    "output_dir": "output_dir",
                                    "save_end_of_training": True,
                                    "save_every_n_epochs": 0,
                                    "save_every_n_steps": 0,
                                    "type": "type",
                                }
                            ],
                            "data": {
                                "beta": 0,
                                "cache_dir": "cache_dir",
                                "cache_fs_type": "cache_fs_type",
                                "dl_num_workers": 0,
                                "eval_sources": [
                                    {
                                        "max_samples": 0,
                                        "name_or_path": "name_or_path",
                                        "process": True,
                                        "sample_count": 0,
                                        "sample_ratio": 0,
                                        "sample_seed": 0,
                                        "split": "split",
                                        "type": "type",
                                    }
                                ],
                                "max_length": 0,
                                "num_proc": 0,
                                "seed": 0,
                                "sources": [
                                    {
                                        "max_samples": 0,
                                        "name_or_path": "name_or_path",
                                        "process": True,
                                        "sample_count": 0,
                                        "sample_ratio": 0,
                                        "sample_seed": 0,
                                        "split": "split",
                                        "type": "type",
                                    }
                                ],
                                "temperature": 0,
                                "train_eval_split": [0],
                                "type": "type",
                                "use_data_cache": True,
                            },
                            "datasets": [
                                {
                                    "target": "target",
                                    "weight": 0,
                                }
                            ],
                            "deepspeed": {"zero_optimization": {"stage": 0}},
                            "epochs": 5,
                            "eval_interval": 0,
                            "gradient_accumulation_steps": 0,
                            "micro_batch_size": 16,
                            "model": {
                                "attn_implementation": "attn_implementation",
                                "baked_adapter_config": {
                                    "bias": "bias",
                                    "lora_alpha": 0,
                                    "lora_dropout": 0,
                                    "r": 0,
                                    "target_modules": "target_modules",
                                },
                                "disable_activation_checkpoint": True,
                                "dtype": "dtype",
                                "parent_model_name": "parent_model_name",
                                "peft_config": {"foo": "bar"},
                                "save_name": "save_name",
                                "type": "type",
                            },
                            "model_name": "model_name",
                            "optimizer": {
                                "betas": [{}, {}],
                                "learning_rate": 0,
                                "type": "type",
                                "weight_decay": 0,
                            },
                            "scheduler": {
                                "lr": 0,
                                "type": "type",
                            },
                            "seed": 0,
                            "total_trajectories": 0,
                            "train_log_iter_interval": 0,
                            "type": "type",
                            "wandb": {
                                "enable": True,
                                "entity": "entity",
                                "name": "name",
                                "project": "project",
                            },
                        },
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                        "overrides": {
                            "checkpoint": [
                                {
                                    "auto_resume": True,
                                    "enabled": True,
                                    "output_dir": "output_dir",
                                    "save_end_of_training": True,
                                    "save_every_n_epochs": 0,
                                    "save_every_n_steps": 0,
                                    "type": "type",
                                }
                            ],
                            "data": {
                                "beta": 0,
                                "cache_dir": "cache_dir",
                                "cache_fs_type": "cache_fs_type",
                                "dl_num_workers": 0,
                                "eval_sources": [
                                    {
                                        "max_samples": 0,
                                        "name_or_path": "name_or_path",
                                        "process": True,
                                        "sample_count": 0,
                                        "sample_ratio": 0,
                                        "sample_seed": 0,
                                        "split": "split",
                                        "type": "type",
                                    }
                                ],
                                "max_length": 0,
                                "num_proc": 0,
                                "seed": 0,
                                "sources": [
                                    {
                                        "max_samples": 0,
                                        "name_or_path": "name_or_path",
                                        "process": True,
                                        "sample_count": 0,
                                        "sample_ratio": 0,
                                        "sample_seed": 0,
                                        "split": "split",
                                        "type": "type",
                                    }
                                ],
                                "temperature": 0,
                                "train_eval_split": [0],
                                "type": "type",
                                "use_data_cache": True,
                            },
                            "datasets": [
                                {
                                    "target": "target",
                                    "weight": 0,
                                }
                            ],
                            "deepspeed": {"zero_optimization": {"stage": 0}},
                            "epochs": 0,
                            "eval_interval": 0,
                            "gradient_accumulation_steps": 0,
                            "micro_batch_size": 0,
                            "model": {
                                "attn_implementation": "attn_implementation",
                                "baked_adapter_config": {
                                    "bias": "bias",
                                    "lora_alpha": 0,
                                    "lora_dropout": 0,
                                    "r": 0,
                                    "target_modules": "target_modules",
                                },
                                "disable_activation_checkpoint": True,
                                "dtype": "dtype",
                                "parent_model_name": "parent_model_name",
                                "peft_config": {"foo": "bar"},
                                "save_name": "save_name",
                                "type": "type",
                            },
                            "model_name": "model_name",
                            "optimizer": {
                                "betas": [{}, {}],
                                "learning_rate": 0.001,
                                "type": "type",
                                "weight_decay": 0,
                            },
                            "scheduler": {
                                "lr": 0,
                                "type": "type",
                            },
                            "seed": 0,
                            "total_trajectories": 0,
                            "train_log_iter_interval": 0,
                            "type": "type",
                            "wandb": {
                                "enable": True,
                                "entity": "entity",
                                "name": "name",
                                "project": "project",
                            },
                        },
                    },
                ],
                user_id="user_id",
                x_user_id="X-User-Id",
            )

        assert_matches_type(BakeBatchSetResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.bakes.with_raw_response.batch_set(
                repo_name="repo_name",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                    },
                ],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(BakeBatchSetResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.bakes.with_streaming_response.batch_set(
                repo_name="repo_name",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                    },
                ],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                bake = await response.parse()
                assert_matches_type(BakeBatchSetResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                await async_client.bakes.with_raw_response.batch_set(
                    repo_name="",
                    bakes=[
                        {
                            "bake_name": "bake_v1",
                            "template": "default",
                        },
                        {
                            "bake_name": "bake_v2",
                            "template": "bake_v1",
                        },
                    ],
                )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_batch(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.create_batch(
            repo_name="repo_name",
            bakes=[
                {
                    "bake_name": "bake_v1",
                    "template": "default",
                },
                {
                    "bake_name": "bake_v2",
                    "template": "bake_v1",
                },
            ],
        )
        assert_matches_type(BakeCreateBatchResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_batch_with_all_params(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.create_batch(
            repo_name="repo_name",
            bakes=[
                {
                    "bake_name": "bake_v1",
                    "template": "default",
                    "overrides": {
                        "checkpoint": [
                            {
                                "auto_resume": True,
                                "enabled": True,
                                "output_dir": "output_dir",
                                "save_end_of_training": True,
                                "save_every_n_epochs": 0,
                                "save_every_n_steps": 0,
                                "type": "type",
                            }
                        ],
                        "data": {
                            "beta": 0,
                            "cache_dir": "cache_dir",
                            "cache_fs_type": "cache_fs_type",
                            "dl_num_workers": 0,
                            "eval_sources": [
                                {
                                    "max_samples": 0,
                                    "name_or_path": "name_or_path",
                                    "process": True,
                                    "sample_count": 0,
                                    "sample_ratio": 0,
                                    "sample_seed": 0,
                                    "split": "split",
                                    "type": "type",
                                }
                            ],
                            "max_length": 0,
                            "num_proc": 0,
                            "seed": 0,
                            "sources": [
                                {
                                    "max_samples": 0,
                                    "name_or_path": "name_or_path",
                                    "process": True,
                                    "sample_count": 0,
                                    "sample_ratio": 0,
                                    "sample_seed": 0,
                                    "split": "split",
                                    "type": "type",
                                }
                            ],
                            "temperature": 0,
                            "train_eval_split": [0],
                            "type": "type",
                            "use_data_cache": True,
                        },
                        "datasets": [
                            {
                                "target": "target",
                                "weight": 0,
                            }
                        ],
                        "deepspeed": {"zero_optimization": {"stage": 0}},
                        "epochs": 5,
                        "eval_interval": 0,
                        "gradient_accumulation_steps": 0,
                        "micro_batch_size": 16,
                        "model": {
                            "attn_implementation": "attn_implementation",
                            "baked_adapter_config": {
                                "bias": "bias",
                                "lora_alpha": 0,
                                "lora_dropout": 0,
                                "r": 0,
                                "target_modules": "target_modules",
                            },
                            "disable_activation_checkpoint": True,
                            "dtype": "dtype",
                            "parent_model_name": "parent_model_name",
                            "peft_config": {"foo": "bar"},
                            "save_name": "save_name",
                            "type": "type",
                        },
                        "model_name": "model_name",
                        "optimizer": {
                            "betas": [{}, {}],
                            "learning_rate": 0,
                            "type": "type",
                            "weight_decay": 0,
                        },
                        "scheduler": {
                            "lr": 0,
                            "type": "type",
                        },
                        "seed": 0,
                        "total_trajectories": 0,
                        "train_log_iter_interval": 0,
                        "type": "type",
                        "wandb": {
                            "enable": True,
                            "entity": "entity",
                            "name": "name",
                            "project": "project",
                        },
                    },
                },
                {
                    "bake_name": "bake_v2",
                    "template": "bake_v1",
                    "overrides": {
                        "checkpoint": [
                            {
                                "auto_resume": True,
                                "enabled": True,
                                "output_dir": "output_dir",
                                "save_end_of_training": True,
                                "save_every_n_epochs": 0,
                                "save_every_n_steps": 0,
                                "type": "type",
                            }
                        ],
                        "data": {
                            "beta": 0,
                            "cache_dir": "cache_dir",
                            "cache_fs_type": "cache_fs_type",
                            "dl_num_workers": 0,
                            "eval_sources": [
                                {
                                    "max_samples": 0,
                                    "name_or_path": "name_or_path",
                                    "process": True,
                                    "sample_count": 0,
                                    "sample_ratio": 0,
                                    "sample_seed": 0,
                                    "split": "split",
                                    "type": "type",
                                }
                            ],
                            "max_length": 0,
                            "num_proc": 0,
                            "seed": 0,
                            "sources": [
                                {
                                    "max_samples": 0,
                                    "name_or_path": "name_or_path",
                                    "process": True,
                                    "sample_count": 0,
                                    "sample_ratio": 0,
                                    "sample_seed": 0,
                                    "split": "split",
                                    "type": "type",
                                }
                            ],
                            "temperature": 0,
                            "train_eval_split": [0],
                            "type": "type",
                            "use_data_cache": True,
                        },
                        "datasets": [
                            {
                                "target": "target",
                                "weight": 0,
                            }
                        ],
                        "deepspeed": {"zero_optimization": {"stage": 0}},
                        "epochs": 0,
                        "eval_interval": 0,
                        "gradient_accumulation_steps": 0,
                        "micro_batch_size": 0,
                        "model": {
                            "attn_implementation": "attn_implementation",
                            "baked_adapter_config": {
                                "bias": "bias",
                                "lora_alpha": 0,
                                "lora_dropout": 0,
                                "r": 0,
                                "target_modules": "target_modules",
                            },
                            "disable_activation_checkpoint": True,
                            "dtype": "dtype",
                            "parent_model_name": "parent_model_name",
                            "peft_config": {"foo": "bar"},
                            "save_name": "save_name",
                            "type": "type",
                        },
                        "model_name": "model_name",
                        "optimizer": {
                            "betas": [{}, {}],
                            "learning_rate": 0.001,
                            "type": "type",
                            "weight_decay": 0,
                        },
                        "scheduler": {
                            "lr": 0,
                            "type": "type",
                        },
                        "seed": 0,
                        "total_trajectories": 0,
                        "train_log_iter_interval": 0,
                        "type": "type",
                        "wandb": {
                            "enable": True,
                            "entity": "entity",
                            "name": "name",
                            "project": "project",
                        },
                    },
                },
            ],
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeCreateBatchResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_batch(self, async_client: AsyncBread) -> None:
        response = await async_client.bakes.with_raw_response.create_batch(
            repo_name="repo_name",
            bakes=[
                {
                    "bake_name": "bake_v1",
                    "template": "default",
                },
                {
                    "bake_name": "bake_v2",
                    "template": "bake_v1",
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(BakeCreateBatchResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_batch(self, async_client: AsyncBread) -> None:
        async with async_client.bakes.with_streaming_response.create_batch(
            repo_name="repo_name",
            bakes=[
                {
                    "bake_name": "bake_v1",
                    "template": "default",
                },
                {
                    "bake_name": "bake_v2",
                    "template": "bake_v1",
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = await response.parse()
            assert_matches_type(BakeCreateBatchResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_batch(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.bakes.with_raw_response.create_batch(
                repo_name="",
                bakes=[
                    {
                        "bake_name": "bake_v1",
                        "template": "default",
                    },
                    {
                        "bake_name": "bake_v2",
                        "template": "bake_v1",
                    },
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_download(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.download(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(BakeDownloadResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_download_with_all_params(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.download(
            bake_name="bake_name",
            repo_name="repo_name",
            checkpoint=0,
            expires_in=1,
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeDownloadResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_download(self, async_client: AsyncBread) -> None:
        response = await async_client.bakes.with_raw_response.download(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(BakeDownloadResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_download(self, async_client: AsyncBread) -> None:
        async with async_client.bakes.with_streaming_response.download(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = await response.parse()
            assert_matches_type(BakeDownloadResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_download(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.bakes.with_raw_response.download(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            await async_client.bakes.with_raw_response.download(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.get(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.get(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncBread) -> None:
        response = await async_client.bakes.with_raw_response.get(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncBread) -> None:
        async with async_client.bakes.with_streaming_response.get(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = await response.parse()
            assert_matches_type(BakeResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.bakes.with_raw_response.get(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            await async_client.bakes.with_raw_response.get(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_metrics(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.get_metrics(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(BakeGetMetricsResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_metrics_with_all_params(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.get_metrics(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeGetMetricsResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_metrics(self, async_client: AsyncBread) -> None:
        response = await async_client.bakes.with_raw_response.get_metrics(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(BakeGetMetricsResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_metrics(self, async_client: AsyncBread) -> None:
        async with async_client.bakes.with_streaming_response.get_metrics(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = await response.parse()
            assert_matches_type(BakeGetMetricsResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_metrics(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.bakes.with_raw_response.get_metrics(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            await async_client.bakes.with_raw_response.get_metrics(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.run(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncBread) -> None:
        bake = await async_client.bakes.run(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncBread) -> None:
        response = await async_client.bakes.with_raw_response.run(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncBread) -> None:
        async with async_client.bakes.with_streaming_response.run(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bake = await response.parse()
            assert_matches_type(BakeResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_run(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.bakes.with_raw_response.run(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            await async_client.bakes.with_raw_response.run(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            bake = await async_client.bakes.set(
                bake_name="bake_name",
                repo_name="repo_name",
                template="template",
            )

        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_with_all_params(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            bake = await async_client.bakes.set(
                bake_name="bake_name",
                repo_name="repo_name",
                template="template",
                user_id="user_id",
                overrides={
                    "checkpoint": [
                        {
                            "auto_resume": True,
                            "enabled": True,
                            "output_dir": "output_dir",
                            "save_end_of_training": True,
                            "save_every_n_epochs": 0,
                            "save_every_n_steps": 0,
                            "type": "type",
                        }
                    ],
                    "data": {
                        "beta": 0,
                        "cache_dir": "cache_dir",
                        "cache_fs_type": "cache_fs_type",
                        "dl_num_workers": 0,
                        "eval_sources": [
                            {
                                "max_samples": 0,
                                "name_or_path": "name_or_path",
                                "process": True,
                                "sample_count": 0,
                                "sample_ratio": 0,
                                "sample_seed": 0,
                                "split": "split",
                                "type": "type",
                            }
                        ],
                        "max_length": 0,
                        "num_proc": 0,
                        "seed": 0,
                        "sources": [
                            {
                                "max_samples": 0,
                                "name_or_path": "name_or_path",
                                "process": True,
                                "sample_count": 0,
                                "sample_ratio": 0,
                                "sample_seed": 0,
                                "split": "split",
                                "type": "type",
                            }
                        ],
                        "temperature": 0,
                        "train_eval_split": [0],
                        "type": "type",
                        "use_data_cache": True,
                    },
                    "datasets": [
                        {
                            "target": "target",
                            "weight": 0,
                        }
                    ],
                    "deepspeed": {"zero_optimization": {"stage": 0}},
                    "epochs": 0,
                    "eval_interval": 0,
                    "gradient_accumulation_steps": 0,
                    "micro_batch_size": 0,
                    "model": {
                        "attn_implementation": "attn_implementation",
                        "baked_adapter_config": {
                            "bias": "bias",
                            "lora_alpha": 0,
                            "lora_dropout": 0,
                            "r": 0,
                            "target_modules": "target_modules",
                        },
                        "disable_activation_checkpoint": True,
                        "dtype": "dtype",
                        "parent_model_name": "parent_model_name",
                        "peft_config": {"foo": "bar"},
                        "save_name": "save_name",
                        "type": "type",
                    },
                    "model_name": "model_name",
                    "optimizer": {
                        "betas": [{}, {}],
                        "learning_rate": 0,
                        "type": "type",
                        "weight_decay": 0,
                    },
                    "scheduler": {
                        "lr": 0,
                        "type": "type",
                    },
                    "seed": 0,
                    "total_trajectories": 0,
                    "train_log_iter_interval": 0,
                    "type": "type",
                    "wandb": {
                        "enable": True,
                        "entity": "entity",
                        "name": "name",
                        "project": "project",
                    },
                },
                x_user_id="X-User-Id",
            )

        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.bakes.with_raw_response.set(
                bake_name="bake_name",
                repo_name="repo_name",
                template="template",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bake = await response.parse()
        assert_matches_type(BakeResponse, bake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.bakes.with_streaming_response.set(
                bake_name="bake_name",
                repo_name="repo_name",
                template="template",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                bake = await response.parse()
                assert_matches_type(BakeResponse, bake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                await async_client.bakes.with_raw_response.set(
                    bake_name="bake_name",
                    repo_name="",
                    template="template",
                )

            with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
                await async_client.bakes.with_raw_response.set(
                    bake_name="",
                    repo_name="repo_name",
                    template="template",
                )
