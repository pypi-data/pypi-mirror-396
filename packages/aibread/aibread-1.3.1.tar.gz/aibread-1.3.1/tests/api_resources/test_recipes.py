# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from aibread import Bread, AsyncBread
from tests.utils import assert_matches_type
from aibread.types import (
    RecipeGetRecreationPlanResponse,
    RecipeGetDependencyGraphResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRecipes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_dependency_graph(self, client: Bread) -> None:
        recipe = client.recipes.get_dependency_graph(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(RecipeGetDependencyGraphResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_dependency_graph_with_all_params(self, client: Bread) -> None:
        recipe = client.recipes.get_dependency_graph(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RecipeGetDependencyGraphResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_dependency_graph(self, client: Bread) -> None:
        response = client.recipes.with_raw_response.get_dependency_graph(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recipe = response.parse()
        assert_matches_type(RecipeGetDependencyGraphResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_dependency_graph(self, client: Bread) -> None:
        with client.recipes.with_streaming_response.get_dependency_graph(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recipe = response.parse()
            assert_matches_type(RecipeGetDependencyGraphResponse, recipe, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_dependency_graph(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.recipes.with_raw_response.get_dependency_graph(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            client.recipes.with_raw_response.get_dependency_graph(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_recreation_plan(self, client: Bread) -> None:
        recipe = client.recipes.get_recreation_plan(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(RecipeGetRecreationPlanResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_recreation_plan_with_all_params(self, client: Bread) -> None:
        recipe = client.recipes.get_recreation_plan(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RecipeGetRecreationPlanResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_recreation_plan(self, client: Bread) -> None:
        response = client.recipes.with_raw_response.get_recreation_plan(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recipe = response.parse()
        assert_matches_type(RecipeGetRecreationPlanResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_recreation_plan(self, client: Bread) -> None:
        with client.recipes.with_streaming_response.get_recreation_plan(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recipe = response.parse()
            assert_matches_type(RecipeGetRecreationPlanResponse, recipe, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_recreation_plan(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.recipes.with_raw_response.get_recreation_plan(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            client.recipes.with_raw_response.get_recreation_plan(
                bake_name="",
                repo_name="repo_name",
            )


class TestAsyncRecipes:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_dependency_graph(self, async_client: AsyncBread) -> None:
        recipe = await async_client.recipes.get_dependency_graph(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(RecipeGetDependencyGraphResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_dependency_graph_with_all_params(self, async_client: AsyncBread) -> None:
        recipe = await async_client.recipes.get_dependency_graph(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RecipeGetDependencyGraphResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_dependency_graph(self, async_client: AsyncBread) -> None:
        response = await async_client.recipes.with_raw_response.get_dependency_graph(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recipe = await response.parse()
        assert_matches_type(RecipeGetDependencyGraphResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_dependency_graph(self, async_client: AsyncBread) -> None:
        async with async_client.recipes.with_streaming_response.get_dependency_graph(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recipe = await response.parse()
            assert_matches_type(RecipeGetDependencyGraphResponse, recipe, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_dependency_graph(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.recipes.with_raw_response.get_dependency_graph(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            await async_client.recipes.with_raw_response.get_dependency_graph(
                bake_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_recreation_plan(self, async_client: AsyncBread) -> None:
        recipe = await async_client.recipes.get_recreation_plan(
            bake_name="bake_name",
            repo_name="repo_name",
        )
        assert_matches_type(RecipeGetRecreationPlanResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_recreation_plan_with_all_params(self, async_client: AsyncBread) -> None:
        recipe = await async_client.recipes.get_recreation_plan(
            bake_name="bake_name",
            repo_name="repo_name",
            user_id="user_id",
            x_user_id="X-User-Id",
        )
        assert_matches_type(RecipeGetRecreationPlanResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_recreation_plan(self, async_client: AsyncBread) -> None:
        response = await async_client.recipes.with_raw_response.get_recreation_plan(
            bake_name="bake_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recipe = await response.parse()
        assert_matches_type(RecipeGetRecreationPlanResponse, recipe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_recreation_plan(self, async_client: AsyncBread) -> None:
        async with async_client.recipes.with_streaming_response.get_recreation_plan(
            bake_name="bake_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recipe = await response.parse()
            assert_matches_type(RecipeGetRecreationPlanResponse, recipe, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_recreation_plan(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.recipes.with_raw_response.get_recreation_plan(
                bake_name="bake_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `bake_name` but received ''"):
            await async_client.recipes.with_raw_response.get_recreation_plan(
                bake_name="",
                repo_name="repo_name",
            )
