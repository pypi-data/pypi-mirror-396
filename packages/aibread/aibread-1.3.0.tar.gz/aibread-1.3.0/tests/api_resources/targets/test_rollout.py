# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from aibread import Bread, AsyncBread
from tests.utils import assert_matches_type
from aibread.types.targets import (
    RolloutResponse,
    RolloutGetOutputResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRollout:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Bread) -> None:
        rollout = client.targets.rollout.get(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Bread) -> None:
        rollout = client.targets.rollout.get(
            target_name="target_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Bread) -> None:
        response = client.targets.rollout.with_raw_response.get(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Bread) -> None:
        with client.targets.rollout.with_streaming_response.get(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(RolloutResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.targets.rollout.with_raw_response.get(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            client.targets.rollout.with_raw_response.get(
                target_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_output(self, client: Bread) -> None:
        rollout = client.targets.rollout.get_output(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(RolloutGetOutputResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_output_with_all_params(self, client: Bread) -> None:
        rollout = client.targets.rollout.get_output(
            target_name="target_name",
            repo_name="repo_name",
            limit=1,
            offset=0,
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RolloutGetOutputResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_output(self, client: Bread) -> None:
        response = client.targets.rollout.with_raw_response.get_output(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(RolloutGetOutputResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_output(self, client: Bread) -> None:
        with client.targets.rollout.with_streaming_response.get_output(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(RolloutGetOutputResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_output(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.targets.rollout.with_raw_response.get_output(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            client.targets.rollout.with_raw_response.get_output(
                target_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run(self, client: Bread) -> None:
        rollout = client.targets.rollout.run(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_with_all_params(self, client: Bread) -> None:
        rollout = client.targets.rollout.run(
            target_name="target_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_run(self, client: Bread) -> None:
        response = client.targets.rollout.with_raw_response.run(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_run(self, client: Bread) -> None:
        with client.targets.rollout.with_streaming_response.run(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(RolloutResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_run(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.targets.rollout.with_raw_response.run(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            client.targets.rollout.with_raw_response.run(
                target_name="",
                repo_name="repo_name",
            )


class TestAsyncRollout:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncBread) -> None:
        rollout = await async_client.targets.rollout.get(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncBread) -> None:
        rollout = await async_client.targets.rollout.get(
            target_name="target_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncBread) -> None:
        response = await async_client.targets.rollout.with_raw_response.get(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncBread) -> None:
        async with async_client.targets.rollout.with_streaming_response.get(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(RolloutResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.targets.rollout.with_raw_response.get(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            await async_client.targets.rollout.with_raw_response.get(
                target_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_output(self, async_client: AsyncBread) -> None:
        rollout = await async_client.targets.rollout.get_output(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(RolloutGetOutputResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_output_with_all_params(self, async_client: AsyncBread) -> None:
        rollout = await async_client.targets.rollout.get_output(
            target_name="target_name",
            repo_name="repo_name",
            limit=1,
            offset=0,
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RolloutGetOutputResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_output(self, async_client: AsyncBread) -> None:
        response = await async_client.targets.rollout.with_raw_response.get_output(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(RolloutGetOutputResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_output(self, async_client: AsyncBread) -> None:
        async with async_client.targets.rollout.with_streaming_response.get_output(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(RolloutGetOutputResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_output(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.targets.rollout.with_raw_response.get_output(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            await async_client.targets.rollout.with_raw_response.get_output(
                target_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run(self, async_client: AsyncBread) -> None:
        rollout = await async_client.targets.rollout.run(
            target_name="target_name",
            repo_name="repo_name",
        )
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncBread) -> None:
        rollout = await async_client.targets.rollout.run(
            target_name="target_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncBread) -> None:
        response = await async_client.targets.rollout.with_raw_response.run(
            target_name="target_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(RolloutResponse, rollout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncBread) -> None:
        async with async_client.targets.rollout.with_streaming_response.run(
            target_name="target_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(RolloutResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_run(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.targets.rollout.with_raw_response.run(
                target_name="target_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `target_name` but received ''"):
            await async_client.targets.rollout.with_raw_response.run(
                target_name="",
                repo_name="repo_name",
            )
