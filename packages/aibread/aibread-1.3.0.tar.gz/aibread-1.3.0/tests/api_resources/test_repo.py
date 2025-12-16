# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from aibread import Bread, AsyncBread
from tests.utils import assert_matches_type
from aibread.types import (
    RepoResponse,
    RepoListResponse,
    RepoGetTreeResponse,
)

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRepo:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Bread) -> None:
        repo = client.repo.create(
            repo_name="repo_name",
        )
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Bread) -> None:
        repo = client.repo.create(
            repo_name="repo_name",
            user_id="user_id",
            base_model="base_model",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Bread) -> None:
        response = client.repo.with_raw_response.create(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Bread) -> None:
        with client.repo.with_streaming_response.create(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Bread) -> None:
        repo = client.repo.list()
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Bread) -> None:
        repo = client.repo.list(
            include_metadata=True,
            limit=1,
            offset=0,
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Bread) -> None:
        response = client.repo.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Bread) -> None:
        with client.repo.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoListResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Bread) -> None:
        repo = client.repo.get(
            repo_name="repo_name",
        )
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Bread) -> None:
        repo = client.repo.get(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Bread) -> None:
        response = client.repo.with_raw_response.get(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Bread) -> None:
        with client.repo.with_streaming_response.get(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.repo.with_raw_response.get(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_tree(self, client: Bread) -> None:
        repo = client.repo.get_tree(
            repo_name="repo_name",
        )
        assert_matches_type(RepoGetTreeResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_tree_with_all_params(self, client: Bread) -> None:
        repo = client.repo.get_tree(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RepoGetTreeResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_tree(self, client: Bread) -> None:
        response = client.repo.with_raw_response.get_tree(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoGetTreeResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_tree(self, client: Bread) -> None:
        with client.repo.with_streaming_response.get_tree(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = response.parse()
            assert_matches_type(RepoGetTreeResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_tree(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.repo.with_raw_response.get_tree(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            repo = client.repo.set(
                repo_name="repo_name",
            )

        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_with_all_params(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            repo = client.repo.set(
                repo_name="repo_name",
                user_id="user_id",
                base_model="base_model",
                x_user_id="X-User-Id",
            )

        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.repo.with_raw_response.set(
                repo_name="repo_name",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = response.parse()
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set(self, client: Bread) -> None:
        with pytest.warns(DeprecationWarning):
            with client.repo.with_streaming_response.set(
                repo_name="repo_name",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                repo = response.parse()
                assert_matches_type(RepoResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRepo:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncBread) -> None:
        repo = await async_client.repo.create(
            repo_name="repo_name",
        )
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncBread) -> None:
        repo = await async_client.repo.create(
            repo_name="repo_name",
            user_id="user_id",
            base_model="base_model",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBread) -> None:
        response = await async_client.repo.with_raw_response.create(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBread) -> None:
        async with async_client.repo.with_streaming_response.create(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncBread) -> None:
        repo = await async_client.repo.list()
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncBread) -> None:
        repo = await async_client.repo.list(
            include_metadata=True,
            limit=1,
            offset=0,
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBread) -> None:
        response = await async_client.repo.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoListResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBread) -> None:
        async with async_client.repo.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoListResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncBread) -> None:
        repo = await async_client.repo.get(
            repo_name="repo_name",
        )
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncBread) -> None:
        repo = await async_client.repo.get(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncBread) -> None:
        response = await async_client.repo.with_raw_response.get(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncBread) -> None:
        async with async_client.repo.with_streaming_response.get(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.repo.with_raw_response.get(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_tree(self, async_client: AsyncBread) -> None:
        repo = await async_client.repo.get_tree(
            repo_name="repo_name",
        )
        assert_matches_type(RepoGetTreeResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_tree_with_all_params(self, async_client: AsyncBread) -> None:
        repo = await async_client.repo.get_tree(
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RepoGetTreeResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_tree(self, async_client: AsyncBread) -> None:
        response = await async_client.repo.with_raw_response.get_tree(
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoGetTreeResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_tree(self, async_client: AsyncBread) -> None:
        async with async_client.repo.with_streaming_response.get_tree(
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            repo = await response.parse()
            assert_matches_type(RepoGetTreeResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_tree(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.repo.with_raw_response.get_tree(
                repo_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            repo = await async_client.repo.set(
                repo_name="repo_name",
            )

        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_with_all_params(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            repo = await async_client.repo.set(
                repo_name="repo_name",
                user_id="user_id",
                base_model="base_model",
                x_user_id="X-User-Id",
            )

        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.repo.with_raw_response.set(
                repo_name="repo_name",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        repo = await response.parse()
        assert_matches_type(RepoResponse, repo, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set(self, async_client: AsyncBread) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.repo.with_streaming_response.set(
                repo_name="repo_name",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                repo = await response.parse()
                assert_matches_type(RepoResponse, repo, path=["response"])

        assert cast(Any, response.is_closed) is True
