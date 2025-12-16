# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from aibread import Bread, AsyncBread
from tests.utils import assert_matches_type
from aibread.types import (
    PromptResponse,
    PromptListResponse,
    PromptBatchSetResponse,
    PromptCreateBatchResponse,
)

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPrompts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Bread) -> None:
        prompt = client.prompts.create(
            repo_name="repo_name",
            messages=[{"role": "role"}],
            prompt_name="prompt_name",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Bread) -> None:
        prompt = client.prompts.create(
            repo_name="repo_name",
            messages=[
                {
                    "role": "role",
                    "content": "string",
                }
            ],
            prompt_name="prompt_name",
            user_id="user_id",
            tools=[{"foo": "bar"}],
            x_user_id="X-User-Id",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Bread) -> None:
        response = client.prompts.with_raw_response.create(
            repo_name="repo_name",
            messages=[{"role": "role"}],
            prompt_name="prompt_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Bread) -> None:
        with client.prompts.with_streaming_response.create(
            repo_name="repo_name",
            messages=[{"role": "role"}],
            prompt_name="prompt_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = response.parse()
            assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.prompts.with_raw_response.create(
                repo_name="",
                messages=[{"role": "role"}],
                prompt_name="prompt_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Bread) -> None:
        prompt = client.prompts.list(
            repo_name="repo_name",
        )
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Bread) -> None:
        prompt = client.prompts.list(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Bread) -> None:
        response = client.prompts.with_raw_response.list(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Bread) -> None:
        with client.prompts.with_streaming_response.list(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = response.parse()
            assert_matches_type(PromptListResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.prompts.with_raw_response.list(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            prompt = client.prompts.batch_set(
                repo_name="repo_name",
                prompts={"foo": [{"role": "role"}]},
            )

        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_set_with_all_params(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            prompt = client.prompts.batch_set(
                repo_name="repo_name",
                prompts={
                    "foo": [
                        {
                            "role": "role",
                            "content": "string",
                        }
                    ]
                },
                user_id="user_id",
                x_user_id="X-User-Id",
            )

        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.prompts.with_raw_response.batch_set(
                repo_name="repo_name",
                prompts={"foo": [{"role": "role"}]},
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.prompts.with_streaming_response.batch_set(
                repo_name="repo_name",
                prompts={"foo": [{"role": "role"}]},
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                prompt = response.parse()
                assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                client.prompts.with_raw_response.batch_set(
                    repo_name="",
                    prompts={"foo": [{"role": "role"}]},
                )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_batch(self, client: Bread) -> None:
        prompt = client.prompts.create_batch(
            repo_name="repo_name",
            prompts={"foo": [{"role": "role"}]},
        )
        assert_matches_type(PromptCreateBatchResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_batch_with_all_params(self, client: Bread) -> None:
        prompt = client.prompts.create_batch(
            repo_name="repo_name",
            prompts={
                "foo": [
                    {
                        "role": "role",
                        "content": "string",
                    }
                ]
            },
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(PromptCreateBatchResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_batch(self, client: Bread) -> None:
        response = client.prompts.with_raw_response.create_batch(
            repo_name="repo_name",
            prompts={"foo": [{"role": "role"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptCreateBatchResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_batch(self, client: Bread) -> None:
        with client.prompts.with_streaming_response.create_batch(
            repo_name="repo_name",
            prompts={"foo": [{"role": "role"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = response.parse()
            assert_matches_type(PromptCreateBatchResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_batch(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.prompts.with_raw_response.create_batch(
                repo_name="",
                prompts={"foo": [{"role": "role"}]},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Bread) -> None:
        prompt = client.prompts.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Bread) -> None:
        prompt = client.prompts.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Bread) -> None:
        response = client.prompts.with_raw_response.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Bread) -> None:
        with client.prompts.with_streaming_response.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = response.parse()
            assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.prompts.with_raw_response.get(
                prompt_name="prompt_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
            client.prompts.with_raw_response.get(
                prompt_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            prompt = client.prompts.set(
                prompt_name="prompt_name",
                repo_name="repo_name",
                messages=[{"role": "role"}],
            )

        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_with_all_params(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            prompt = client.prompts.set(
                prompt_name="prompt_name",
                repo_name="repo_name",
                messages=[
                    {
                        "role": "role",
                        "content": "string",
                    }
                ],
                user_id="user_id",
                tools=[{"foo": "bar"}],
                x_user_id="X-User-Id",
            )

        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.prompts.with_raw_response.set(
                prompt_name="prompt_name",
                repo_name="repo_name",
                messages=[{"role": "role"}],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.prompts.with_streaming_response.set(
                prompt_name="prompt_name",
                repo_name="repo_name",
                messages=[{"role": "role"}],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                prompt = response.parse()
                assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                client.prompts.with_raw_response.set(
                    prompt_name="prompt_name",
                    repo_name="",
                    messages=[{"role": "role"}],
                )

            with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
                client.prompts.with_raw_response.set(
                    prompt_name="",
                    repo_name="repo_name",
                    messages=[{"role": "role"}],
                )


class TestAsyncPrompts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.create(
            repo_name="repo_name",
            messages=[{"role": "role"}],
            prompt_name="prompt_name",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.create(
            repo_name="repo_name",
            messages=[
                {
                    "role": "role",
                    "content": "string",
                }
            ],
            prompt_name="prompt_name",
            user_id="user_id",
            tools=[{"foo": "bar"}],
            x_user_id="X-User-Id",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBread) -> None:
        response = await async_client.prompts.with_raw_response.create(
            repo_name="repo_name",
            messages=[{"role": "role"}],
            prompt_name="prompt_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBread) -> None:
        async with async_client.prompts.with_streaming_response.create(
            repo_name="repo_name",
            messages=[{"role": "role"}],
            prompt_name="prompt_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = await response.parse()
            assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.prompts.with_raw_response.create(
                repo_name="",
                messages=[{"role": "role"}],
                prompt_name="prompt_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.list(
            repo_name="repo_name",
        )
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.list(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBread) -> None:
        response = await async_client.prompts.with_raw_response.list(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBread) -> None:
        async with async_client.prompts.with_streaming_response.list(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = await response.parse()
            assert_matches_type(PromptListResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.prompts.with_raw_response.list(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            prompt = await async_client.prompts.batch_set(
                repo_name="repo_name",
                prompts={"foo": [{"role": "role"}]},
            )

        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_set_with_all_params(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            prompt = await async_client.prompts.batch_set(
                repo_name="repo_name",
                prompts={
                    "foo": [
                        {
                            "role": "role",
                            "content": "string",
                        }
                    ]
                },
                user_id="user_id",
                x_user_id="X-User-Id",
            )

        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.prompts.with_raw_response.batch_set(
                repo_name="repo_name",
                prompts={"foo": [{"role": "role"}]},
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.prompts.with_streaming_response.batch_set(
                repo_name="repo_name",
                prompts={"foo": [{"role": "role"}]},
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                prompt = await response.parse()
                assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                await async_client.prompts.with_raw_response.batch_set(
                    repo_name="",
                    prompts={"foo": [{"role": "role"}]},
                )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_batch(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.create_batch(
            repo_name="repo_name",
            prompts={"foo": [{"role": "role"}]},
        )
        assert_matches_type(PromptCreateBatchResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_batch_with_all_params(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.create_batch(
            repo_name="repo_name",
            prompts={
                "foo": [
                    {
                        "role": "role",
                        "content": "string",
                    }
                ]
            },
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(PromptCreateBatchResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_batch(self, async_client: AsyncBread) -> None:
        response = await async_client.prompts.with_raw_response.create_batch(
            repo_name="repo_name",
            prompts={"foo": [{"role": "role"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptCreateBatchResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_batch(self, async_client: AsyncBread) -> None:
        async with async_client.prompts.with_streaming_response.create_batch(
            repo_name="repo_name",
            prompts={"foo": [{"role": "role"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = await response.parse()
            assert_matches_type(PromptCreateBatchResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_batch(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.prompts.with_raw_response.create_batch(
                repo_name="",
                prompts={"foo": [{"role": "role"}]},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncBread) -> None:
        response = await async_client.prompts.with_raw_response.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncBread) -> None:
        async with async_client.prompts.with_streaming_response.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = await response.parse()
            assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.prompts.with_raw_response.get(
                prompt_name="prompt_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
            await async_client.prompts.with_raw_response.get(
                prompt_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            prompt = await async_client.prompts.set(
                prompt_name="prompt_name",
                repo_name="repo_name",
                messages=[{"role": "role"}],
            )

        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_with_all_params(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            prompt = await async_client.prompts.set(
                prompt_name="prompt_name",
                repo_name="repo_name",
                messages=[
                    {
                        "role": "role",
                        "content": "string",
                    }
                ],
                user_id="user_id",
                tools=[{"foo": "bar"}],
                x_user_id="X-User-Id",
            )

        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.prompts.with_raw_response.set(
                prompt_name="prompt_name",
                repo_name="repo_name",
                messages=[{"role": "role"}],
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.prompts.with_streaming_response.set(
                prompt_name="prompt_name",
                repo_name="repo_name",
                messages=[{"role": "role"}],
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                prompt = await response.parse()
                assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
                await async_client.prompts.with_raw_response.set(
                    prompt_name="prompt_name",
                    repo_name="",
                    messages=[{"role": "role"}],
                )

            with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
                await async_client.prompts.with_raw_response.set(
                    prompt_name="",
                    repo_name="repo_name",
                    messages=[{"role": "role"}],
                )
