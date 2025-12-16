# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from aibread import Bread, AsyncBread
from tests.utils import assert_matches_type
from aibread.types import (
    DeleteResponse,
    TargetResponse,
    TargetListResponse,
    TargetBatchSetResponse,
    TargetCreateBatchResponse,
)

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTargets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Bread) -> None:
        target = client.targets.create(
            repo_name="repo_name",
            target_name="target_name",
            template="default",
        )
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Bread) -> None:
        target = client.targets.create(
            repo_name="repo_name",
            target_name="target_name",
            template="default",
            user_id="user_id",
            overrides={
                "extra_kwargs": {"foo": "bar"},
                "generators": [
                    {
                        "type": "oneshot_qs",
                        "dataset": "dataset",
                        "max_tokens": 1,
                        "model": "claude-3-5-sonnet-20241022",
                        "numq": 10,
                        "questions": ["string"],
                        "rollout_with_conditioned": True,
                        "seed": 0,
                        "temperature": 1,
                        "template_content": "template_content",
                        "template_path": "template_path",
                    },
                    {
                        "type": "from_dataset",
                        "dataset": "code_contests",
                        "max_tokens": 1,
                        "model": "model",
                        "numq": 15,
                        "questions": ["string"],
                        "rollout_with_conditioned": True,
                        "seed": 42,
                        "temperature": 0,
                        "template_content": "template_content",
                        "template_path": "template_path",
                    },
                    {
                        "type": "hardcoded",
                        "dataset": "dataset",
                        "max_tokens": 1,
                        "model": "model",
                        "numq": 1,
                        "questions": [
                            "Write a function to reverse a string",
                            "Implement binary search",
                            "Create a linked list class",
                        ],
                        "rollout_with_conditioned": False,
                        "seed": 0,
                        "temperature": 0,
                        "template_content": "template_content",
                        "template_path": "template_path",
                    },
                    {
                        "type": "persona",
                        "dataset": "dataset",
                        "max_tokens": 1,
                        "model": "model",
                        "numq": 5,
                        "questions": ["string"],
                        "rollout_with_conditioned": True,
                        "seed": 123,
                        "temperature": 0.9,
                        "template_content": "template_content",
                        "template_path": "template_path",
                    },
                ],
                "max_concurrency": 50,
                "max_tokens": 150,
                "model_name": "Qwen/Qwen3-32B",
                "num_traj_per_stimulus": 5,
                "student_prompt": "user_prompt_v1",
                "teacher_prompt": "system_prompt_v1",
                "temperature": 1,
                "u": "u",
                "v": "v",
            },
            x_user_id="X-User-Id",
        )
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Bread) -> None:
        response = client.targets.with_raw_response.create(
            repo_name="repo_name",
            target_name="target_name",
            template="default",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Bread) -> None:
        with client.targets.with_streaming_response.create(
            repo_name="repo_name",
            target_name="target_name",
            template="default",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(TargetResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.targets.with_raw_response.create(
                repo_name="",
                target_name="target_name",
                template="default",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Bread) -> None:
        target = client.targets.list(
            repo_name="repo_name",
        )
        assert_matches_type(TargetListResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Bread) -> None:
        target = client.targets.list(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(TargetListResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Bread) -> None:
        response = client.targets.with_raw_response.list(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(TargetListResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Bread) -> None:
        with client.targets.with_streaming_response.list(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(TargetListResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.targets.with_raw_response.list(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Bread) -> None:
        target = client.targets.delete(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(DeleteResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: Bread) -> None:
        target = client.targets.delete(
            target_name="target_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(DeleteResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Bread) -> None:
        response = client.targets.with_raw_response.delete(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(DeleteResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Bread) -> None:
        with client.targets.with_streaming_response.delete(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(DeleteResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.targets.with_raw_response.delete(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            client.targets.with_raw_response.delete(
                target_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            target = client.targets.batch_set(
                repo_name="repo_name",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                    },
                ],
            )

        assert_matches_type(TargetBatchSetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_set_with_all_params(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            target = client.targets.batch_set(
                repo_name="repo_name",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                        "overrides": {
                            "extra_kwargs": {"foo": "bar"},
                            "generators": [
                                {
                                    "type": "type",
                                    "dataset": "dataset",
                                    "max_tokens": 1,
                                    "model": "model",
                                    "numq": 1,
                                    "questions": ["string"],
                                    "rollout_with_conditioned": True,
                                    "seed": 0,
                                    "temperature": 0,
                                    "template_content": "template_content",
                                    "template_path": "template_path",
                                }
                            ],
                            "max_concurrency": 1,
                            "max_tokens": 1,
                            "model_name": "model_name",
                            "num_traj_per_stimulus": 1,
                            "student_prompt": "student_prompt",
                            "teacher_prompt": "teacher_prompt",
                            "temperature": 0.8,
                            "u": "my_unconditioned_prompt",
                            "v": "v",
                        },
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                        "overrides": {
                            "extra_kwargs": {"foo": "bar"},
                            "generators": [
                                {
                                    "type": "type",
                                    "dataset": "dataset",
                                    "max_tokens": 1,
                                    "model": "model",
                                    "numq": 1,
                                    "questions": ["string"],
                                    "rollout_with_conditioned": True,
                                    "seed": 0,
                                    "temperature": 0,
                                    "template_content": "template_content",
                                    "template_path": "template_path",
                                }
                            ],
                            "max_concurrency": 1,
                            "max_tokens": 1,
                            "model_name": "model_name",
                            "num_traj_per_stimulus": 1,
                            "student_prompt": "student_prompt",
                            "teacher_prompt": "teacher_prompt",
                            "temperature": 0,
                            "u": "u",
                            "v": "my_conditioned_prompt",
                        },
                    },
                ],
                user_id="user_id",
                x_user_id="X-User-Id",
            )

        assert_matches_type(TargetBatchSetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.targets.with_raw_response.batch_set(
                repo_name="repo_name",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                    },
                ],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(TargetBatchSetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.targets.with_streaming_response.batch_set(
                repo_name="repo_name",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                    },
                ],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                target = response.parse()
                assert_matches_type(TargetBatchSetResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                client.targets.with_raw_response.batch_set(
                    repo_name="",
                    targets=[
                        {
                            "target_name": "target_alpha",
                            "template": "default",
                        },
                        {
                            "target_name": "target_beta",
                            "template": "target_alpha",
                        },
                    ],
                )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_batch(self, client: Bread) -> None:
        target = client.targets.create_batch(
            repo_name="repo_name",
            targets=[
                {
                    "target_name": "target_alpha",
                    "template": "default",
                },
                {
                    "target_name": "target_beta",
                    "template": "target_alpha",
                },
            ],
        )
        assert_matches_type(TargetCreateBatchResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_batch_with_all_params(self, client: Bread) -> None:
        target = client.targets.create_batch(
            repo_name="repo_name",
            targets=[
                {
                    "target_name": "target_alpha",
                    "template": "default",
                    "overrides": {
                        "extra_kwargs": {"foo": "bar"},
                        "generators": [
                            {
                                "type": "type",
                                "dataset": "dataset",
                                "max_tokens": 1,
                                "model": "model",
                                "numq": 1,
                                "questions": ["string"],
                                "rollout_with_conditioned": True,
                                "seed": 0,
                                "temperature": 0,
                                "template_content": "template_content",
                                "template_path": "template_path",
                            }
                        ],
                        "max_concurrency": 1,
                        "max_tokens": 1,
                        "model_name": "model_name",
                        "num_traj_per_stimulus": 1,
                        "student_prompt": "student_prompt",
                        "teacher_prompt": "teacher_prompt",
                        "temperature": 0.8,
                        "u": "my_unconditioned_prompt",
                        "v": "v",
                    },
                },
                {
                    "target_name": "target_beta",
                    "template": "target_alpha",
                    "overrides": {
                        "extra_kwargs": {"foo": "bar"},
                        "generators": [
                            {
                                "type": "type",
                                "dataset": "dataset",
                                "max_tokens": 1,
                                "model": "model",
                                "numq": 1,
                                "questions": ["string"],
                                "rollout_with_conditioned": True,
                                "seed": 0,
                                "temperature": 0,
                                "template_content": "template_content",
                                "template_path": "template_path",
                            }
                        ],
                        "max_concurrency": 1,
                        "max_tokens": 1,
                        "model_name": "model_name",
                        "num_traj_per_stimulus": 1,
                        "student_prompt": "student_prompt",
                        "teacher_prompt": "teacher_prompt",
                        "temperature": 0,
                        "u": "u",
                        "v": "my_conditioned_prompt",
                    },
                },
            ],
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(TargetCreateBatchResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_batch(self, client: Bread) -> None:
        response = client.targets.with_raw_response.create_batch(
            repo_name="repo_name",
            targets=[
                {
                    "target_name": "target_alpha",
                    "template": "default",
                },
                {
                    "target_name": "target_beta",
                    "template": "target_alpha",
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(TargetCreateBatchResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_batch(self, client: Bread) -> None:
        with client.targets.with_streaming_response.create_batch(
            repo_name="repo_name",
            targets=[
                {
                    "target_name": "target_alpha",
                    "template": "default",
                },
                {
                    "target_name": "target_beta",
                    "template": "target_alpha",
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(TargetCreateBatchResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_batch(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.targets.with_raw_response.create_batch(
                repo_name="",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                    },
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Bread) -> None:
        target = client.targets.get(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Bread) -> None:
        target = client.targets.get(
            target_name="target_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Bread) -> None:
        response = client.targets.with_raw_response.get(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Bread) -> None:
        with client.targets.with_streaming_response.get(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(TargetResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.targets.with_raw_response.get(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            client.targets.with_raw_response.get(
                target_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            target = client.targets.set(
                target_name="target_name",
                repo_name="repo_name",
                template="default",
            )

        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_with_all_params(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            target = client.targets.set(
                target_name="target_name",
                repo_name="repo_name",
                template="default",
                user_id="user_id",
                overrides={
                    "extra_kwargs": {"foo": "bar"},
                    "generators": [
                        {
                            "type": "oneshot_qs",
                            "dataset": "dataset",
                            "max_tokens": 1,
                            "model": "claude-3-5-sonnet-20241022",
                            "numq": 10,
                            "questions": ["string"],
                            "rollout_with_conditioned": True,
                            "seed": 0,
                            "temperature": 1,
                            "template_content": "template_content",
                            "template_path": "template_path",
                        },
                        {
                            "type": "from_dataset",
                            "dataset": "code_contests",
                            "max_tokens": 1,
                            "model": "model",
                            "numq": 15,
                            "questions": ["string"],
                            "rollout_with_conditioned": True,
                            "seed": 42,
                            "temperature": 0,
                            "template_content": "template_content",
                            "template_path": "template_path",
                        },
                        {
                            "type": "hardcoded",
                            "dataset": "dataset",
                            "max_tokens": 1,
                            "model": "model",
                            "numq": 1,
                            "questions": [
                                "Write a function to reverse a string",
                                "Implement binary search",
                                "Create a linked list class",
                            ],
                            "rollout_with_conditioned": False,
                            "seed": 0,
                            "temperature": 0,
                            "template_content": "template_content",
                            "template_path": "template_path",
                        },
                        {
                            "type": "persona",
                            "dataset": "dataset",
                            "max_tokens": 1,
                            "model": "model",
                            "numq": 5,
                            "questions": ["string"],
                            "rollout_with_conditioned": True,
                            "seed": 123,
                            "temperature": 0.9,
                            "template_content": "template_content",
                            "template_path": "template_path",
                        },
                    ],
                    "max_concurrency": 50,
                    "max_tokens": 150,
                    "model_name": "Qwen/Qwen3-32B",
                    "num_traj_per_stimulus": 5,
                    "student_prompt": "user_prompt_v1",
                    "teacher_prompt": "system_prompt_v1",
                    "temperature": 1,
                    "u": "u",
                    "v": "v",
                },
                x_user_id="X-User-Id",
            )

        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.targets.with_raw_response.set(
                target_name="target_name",
                repo_name="repo_name",
                template="default",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.targets.with_streaming_response.set(
                target_name="target_name",
                repo_name="repo_name",
                template="default",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                target = response.parse()
                assert_matches_type(TargetResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                client.targets.with_raw_response.set(
                    target_name="target_name",
                    repo_name="",
                    template="default",
                )

            with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
                client.targets.with_raw_response.set(
                    target_name="",
                    repo_name="repo_name",
                    template="default",
                )


class TestAsyncTargets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.create(
            repo_name="repo_name",
            target_name="target_name",
            template="default",
        )
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.create(
            repo_name="repo_name",
            target_name="target_name",
            template="default",
            user_id="user_id",
            overrides={
                "extra_kwargs": {"foo": "bar"},
                "generators": [
                    {
                        "type": "oneshot_qs",
                        "dataset": "dataset",
                        "max_tokens": 1,
                        "model": "claude-3-5-sonnet-20241022",
                        "numq": 10,
                        "questions": ["string"],
                        "rollout_with_conditioned": True,
                        "seed": 0,
                        "temperature": 1,
                        "template_content": "template_content",
                        "template_path": "template_path",
                    },
                    {
                        "type": "from_dataset",
                        "dataset": "code_contests",
                        "max_tokens": 1,
                        "model": "model",
                        "numq": 15,
                        "questions": ["string"],
                        "rollout_with_conditioned": True,
                        "seed": 42,
                        "temperature": 0,
                        "template_content": "template_content",
                        "template_path": "template_path",
                    },
                    {
                        "type": "hardcoded",
                        "dataset": "dataset",
                        "max_tokens": 1,
                        "model": "model",
                        "numq": 1,
                        "questions": [
                            "Write a function to reverse a string",
                            "Implement binary search",
                            "Create a linked list class",
                        ],
                        "rollout_with_conditioned": False,
                        "seed": 0,
                        "temperature": 0,
                        "template_content": "template_content",
                        "template_path": "template_path",
                    },
                    {
                        "type": "persona",
                        "dataset": "dataset",
                        "max_tokens": 1,
                        "model": "model",
                        "numq": 5,
                        "questions": ["string"],
                        "rollout_with_conditioned": True,
                        "seed": 123,
                        "temperature": 0.9,
                        "template_content": "template_content",
                        "template_path": "template_path",
                    },
                ],
                "max_concurrency": 50,
                "max_tokens": 150,
                "model_name": "Qwen/Qwen3-32B",
                "num_traj_per_stimulus": 5,
                "student_prompt": "user_prompt_v1",
                "teacher_prompt": "system_prompt_v1",
                "temperature": 1,
                "u": "u",
                "v": "v",
            },
            x_user_id="X-User-Id",
        )
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBread) -> None:
        response = await async_client.targets.with_raw_response.create(
            repo_name="repo_name",
            target_name="target_name",
            template="default",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBread) -> None:
        async with async_client.targets.with_streaming_response.create(
            repo_name="repo_name",
            target_name="target_name",
            template="default",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(TargetResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.targets.with_raw_response.create(
                repo_name="",
                target_name="target_name",
                template="default",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.list(
            repo_name="repo_name",
        )
        assert_matches_type(TargetListResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.list(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(TargetListResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBread) -> None:
        response = await async_client.targets.with_raw_response.list(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(TargetListResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBread) -> None:
        async with async_client.targets.with_streaming_response.list(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(TargetListResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.targets.with_raw_response.list(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.delete(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(DeleteResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.delete(
            target_name="target_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(DeleteResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncBread) -> None:
        response = await async_client.targets.with_raw_response.delete(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(DeleteResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncBread) -> None:
        async with async_client.targets.with_streaming_response.delete(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(DeleteResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.targets.with_raw_response.delete(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            await async_client.targets.with_raw_response.delete(
                target_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            target = await async_client.targets.batch_set(
                repo_name="repo_name",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                    },
                ],
            )

        assert_matches_type(TargetBatchSetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_set_with_all_params(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            target = await async_client.targets.batch_set(
                repo_name="repo_name",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                        "overrides": {
                            "extra_kwargs": {"foo": "bar"},
                            "generators": [
                                {
                                    "type": "type",
                                    "dataset": "dataset",
                                    "max_tokens": 1,
                                    "model": "model",
                                    "numq": 1,
                                    "questions": ["string"],
                                    "rollout_with_conditioned": True,
                                    "seed": 0,
                                    "temperature": 0,
                                    "template_content": "template_content",
                                    "template_path": "template_path",
                                }
                            ],
                            "max_concurrency": 1,
                            "max_tokens": 1,
                            "model_name": "model_name",
                            "num_traj_per_stimulus": 1,
                            "student_prompt": "student_prompt",
                            "teacher_prompt": "teacher_prompt",
                            "temperature": 0.8,
                            "u": "my_unconditioned_prompt",
                            "v": "v",
                        },
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                        "overrides": {
                            "extra_kwargs": {"foo": "bar"},
                            "generators": [
                                {
                                    "type": "type",
                                    "dataset": "dataset",
                                    "max_tokens": 1,
                                    "model": "model",
                                    "numq": 1,
                                    "questions": ["string"],
                                    "rollout_with_conditioned": True,
                                    "seed": 0,
                                    "temperature": 0,
                                    "template_content": "template_content",
                                    "template_path": "template_path",
                                }
                            ],
                            "max_concurrency": 1,
                            "max_tokens": 1,
                            "model_name": "model_name",
                            "num_traj_per_stimulus": 1,
                            "student_prompt": "student_prompt",
                            "teacher_prompt": "teacher_prompt",
                            "temperature": 0,
                            "u": "u",
                            "v": "my_conditioned_prompt",
                        },
                    },
                ],
                user_id="user_id",
                x_user_id="X-User-Id",
            )

        assert_matches_type(TargetBatchSetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.targets.with_raw_response.batch_set(
                repo_name="repo_name",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                    },
                ],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(TargetBatchSetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.targets.with_streaming_response.batch_set(
                repo_name="repo_name",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                    },
                ],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                target = await response.parse()
                assert_matches_type(TargetBatchSetResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                await async_client.targets.with_raw_response.batch_set(
                    repo_name="",
                    targets=[
                        {
                            "target_name": "target_alpha",
                            "template": "default",
                        },
                        {
                            "target_name": "target_beta",
                            "template": "target_alpha",
                        },
                    ],
                )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_batch(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.create_batch(
            repo_name="repo_name",
            targets=[
                {
                    "target_name": "target_alpha",
                    "template": "default",
                },
                {
                    "target_name": "target_beta",
                    "template": "target_alpha",
                },
            ],
        )
        assert_matches_type(TargetCreateBatchResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_batch_with_all_params(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.create_batch(
            repo_name="repo_name",
            targets=[
                {
                    "target_name": "target_alpha",
                    "template": "default",
                    "overrides": {
                        "extra_kwargs": {"foo": "bar"},
                        "generators": [
                            {
                                "type": "type",
                                "dataset": "dataset",
                                "max_tokens": 1,
                                "model": "model",
                                "numq": 1,
                                "questions": ["string"],
                                "rollout_with_conditioned": True,
                                "seed": 0,
                                "temperature": 0,
                                "template_content": "template_content",
                                "template_path": "template_path",
                            }
                        ],
                        "max_concurrency": 1,
                        "max_tokens": 1,
                        "model_name": "model_name",
                        "num_traj_per_stimulus": 1,
                        "student_prompt": "student_prompt",
                        "teacher_prompt": "teacher_prompt",
                        "temperature": 0.8,
                        "u": "my_unconditioned_prompt",
                        "v": "v",
                    },
                },
                {
                    "target_name": "target_beta",
                    "template": "target_alpha",
                    "overrides": {
                        "extra_kwargs": {"foo": "bar"},
                        "generators": [
                            {
                                "type": "type",
                                "dataset": "dataset",
                                "max_tokens": 1,
                                "model": "model",
                                "numq": 1,
                                "questions": ["string"],
                                "rollout_with_conditioned": True,
                                "seed": 0,
                                "temperature": 0,
                                "template_content": "template_content",
                                "template_path": "template_path",
                            }
                        ],
                        "max_concurrency": 1,
                        "max_tokens": 1,
                        "model_name": "model_name",
                        "num_traj_per_stimulus": 1,
                        "student_prompt": "student_prompt",
                        "teacher_prompt": "teacher_prompt",
                        "temperature": 0,
                        "u": "u",
                        "v": "my_conditioned_prompt",
                    },
                },
            ],
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(TargetCreateBatchResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_batch(self, async_client: AsyncBread) -> None:
        response = await async_client.targets.with_raw_response.create_batch(
            repo_name="repo_name",
            targets=[
                {
                    "target_name": "target_alpha",
                    "template": "default",
                },
                {
                    "target_name": "target_beta",
                    "template": "target_alpha",
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(TargetCreateBatchResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_batch(self, async_client: AsyncBread) -> None:
        async with async_client.targets.with_streaming_response.create_batch(
            repo_name="repo_name",
            targets=[
                {
                    "target_name": "target_alpha",
                    "template": "default",
                },
                {
                    "target_name": "target_beta",
                    "template": "target_alpha",
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(TargetCreateBatchResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_batch(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.targets.with_raw_response.create_batch(
                repo_name="",
                targets=[
                    {
                        "target_name": "target_alpha",
                        "template": "default",
                    },
                    {
                        "target_name": "target_beta",
                        "template": "target_alpha",
                    },
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.get(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncBread) -> None:
        target = await async_client.targets.get(
            target_name="target_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncBread) -> None:
        response = await async_client.targets.with_raw_response.get(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncBread) -> None:
        async with async_client.targets.with_streaming_response.get(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(TargetResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.targets.with_raw_response.get(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            await async_client.targets.with_raw_response.get(
                target_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            target = await async_client.targets.set(
                target_name="target_name",
                repo_name="repo_name",
                template="default",
            )

        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_with_all_params(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            target = await async_client.targets.set(
                target_name="target_name",
                repo_name="repo_name",
                template="default",
                user_id="user_id",
                overrides={
                    "extra_kwargs": {"foo": "bar"},
                    "generators": [
                        {
                            "type": "oneshot_qs",
                            "dataset": "dataset",
                            "max_tokens": 1,
                            "model": "claude-3-5-sonnet-20241022",
                            "numq": 10,
                            "questions": ["string"],
                            "rollout_with_conditioned": True,
                            "seed": 0,
                            "temperature": 1,
                            "template_content": "template_content",
                            "template_path": "template_path",
                        },
                        {
                            "type": "from_dataset",
                            "dataset": "code_contests",
                            "max_tokens": 1,
                            "model": "model",
                            "numq": 15,
                            "questions": ["string"],
                            "rollout_with_conditioned": True,
                            "seed": 42,
                            "temperature": 0,
                            "template_content": "template_content",
                            "template_path": "template_path",
                        },
                        {
                            "type": "hardcoded",
                            "dataset": "dataset",
                            "max_tokens": 1,
                            "model": "model",
                            "numq": 1,
                            "questions": [
                                "Write a function to reverse a string",
                                "Implement binary search",
                                "Create a linked list class",
                            ],
                            "rollout_with_conditioned": False,
                            "seed": 0,
                            "temperature": 0,
                            "template_content": "template_content",
                            "template_path": "template_path",
                        },
                        {
                            "type": "persona",
                            "dataset": "dataset",
                            "max_tokens": 1,
                            "model": "model",
                            "numq": 5,
                            "questions": ["string"],
                            "rollout_with_conditioned": True,
                            "seed": 123,
                            "temperature": 0.9,
                            "template_content": "template_content",
                            "template_path": "template_path",
                        },
                    ],
                    "max_concurrency": 50,
                    "max_tokens": 150,
                    "model_name": "Qwen/Qwen3-32B",
                    "num_traj_per_stimulus": 5,
                    "student_prompt": "user_prompt_v1",
                    "teacher_prompt": "system_prompt_v1",
                    "temperature": 1,
                    "u": "u",
                    "v": "v",
                },
                x_user_id="X-User-Id",
            )

        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.targets.with_raw_response.set(
                target_name="target_name",
                repo_name="repo_name",
                template="default",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(TargetResponse, target, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.targets.with_streaming_response.set(
                target_name="target_name",
                repo_name="repo_name",
                template="default",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                target = await response.parse()
                assert_matches_type(TargetResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                await async_client.targets.with_raw_response.set(
                    target_name="target_name",
                    repo_name="",
                    template="default",
                )

            with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
                await async_client.targets.with_raw_response.set(
                    target_name="",
                    repo_name="repo_name",
                    template="default",
                )
